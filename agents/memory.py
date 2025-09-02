"""
Memory management system for AI agents.
Provides short-term and long-term memory capabilities for maintaining context.
"""

import time
import json
import logging
from typing import Dict, Any, List, Optional, Union
from collections import deque
from dataclasses import dataclass, asdict
from config.settings import get_config

logger = logging.getLogger(__name__)


@dataclass
class MemoryItem:
    """Represents a single memory item."""
    content: Any
    timestamp: float
    item_type: str
    metadata: Dict[str, Any]
    importance: float  # 0.0 to 1.0
    access_count: int = 0
    last_accessed: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory item to dictionary."""
        return asdict(self)
    
    def update_access(self):
        """Update access statistics."""
        self.access_count += 1
        self.last_accessed = time.time()


class Memory:
    """
    Memory management system for AI agents.
    
    Features:
    - Short-term memory (recent items)
    - Long-term memory (important items)
    - Automatic cleanup and prioritization
    - Context retrieval based on relevance
    """
    
    def __init__(self, max_items: int = None, ttl: int = None):
        """
        Initialize the memory system.
        
        Args:
            max_items: Maximum number of items to store
            ttl: Time-to-live for memory items in seconds
        """
        config = get_config()
        self.max_items = max_items or config["memory_max_size"]
        self.ttl = ttl or config["memory_ttl"]
        
        # Memory storage
        self.short_term = deque(maxlen=self.max_items // 2)  # Recent items
        self.long_term = deque(maxlen=self.max_items // 2)   # Important items
        
        # Index for quick lookups
        self.content_index = {}  # content_hash -> memory_item
        self.type_index = {}     # item_type -> [memory_items]
        
        logger.info(f"Memory system initialized with max_items={self.max_items}, ttl={self.ttl}")
    
    def store(self, content: Any, item_type: str = "general", 
              importance: float = 0.5, metadata: Dict[str, Any] = None) -> str:
        """
        Store a new memory item.
        
        Args:
            content: The content to store
            item_type: Type/category of the memory item
            importance: Importance score (0.0 to 1.0)
            metadata: Additional metadata
            
        Returns:
            Memory item ID
        """
        # Create memory item
        item = MemoryItem(
            content=content,
            timestamp=time.time(),
            item_type=item_type,
            metadata=metadata or {},
            importance=min(max(importance, 0.0), 1.0)  # Clamp to 0.0-1.0
        )
        
        # Generate content hash for indexing
        content_hash = self._hash_content(content)
        
        # Store in appropriate memory tier
        if importance >= 0.7:
            self._store_in_long_term(item, content_hash)
        else:
            self._store_in_short_term(item, content_hash)
        
        # Update indexes
        self._update_indexes(item, content_hash)
        
        # Cleanup if needed
        self._cleanup()
        
        logger.debug(f"Stored memory item: {item_type} (importance: {importance})")
        return content_hash
    
    def retrieve(self, query: str = None, item_type: str = None, 
                 limit: int = 10, min_importance: float = 0.0) -> List[MemoryItem]:
        """
        Retrieve memory items based on criteria.
        
        Args:
            query: Text query to search for (searches in content and metadata)
            item_type: Filter by item type
            limit: Maximum number of items to return
            min_importance: Minimum importance threshold
            
        Returns:
            List of relevant memory items, sorted by relevance
        """
        # Start with all items
        candidates = []
        
        # Add items from both memory tiers
        candidates.extend(self.short_term)
        candidates.extend(self.long_term)
        
        # Filter by type if specified
        if item_type:
            candidates = [item for item in candidates if item.item_type == item_type]
        
        # Filter by importance
        candidates = [item for item in candidates if item.importance >= min_importance]
        
        # Filter by query if specified
        if query:
            candidates = self._filter_by_query(candidates, query)
        
        # Sort by relevance (importance + recency + access frequency)
        candidates.sort(key=lambda x: self._calculate_relevance(x), reverse=True)
        
        # Update access statistics
        for item in candidates[:limit]:
            item.update_access()
        
        # Return top results
        result = candidates[:limit]
        logger.debug(f"Retrieved {len(result)} memory items")
        return result
    
    def get_context(self, recent_count: int = 5, important_count: int = 3) -> Dict[str, Any]:
        """
        Get current context for the agent.
        
        Args:
            recent_count: Number of recent items to include
            important_count: Number of important items to include
            
        Returns:
            Context dictionary with recent and important memories
        """
        # Get recent items
        recent = list(self.short_term)[-recent_count:] if self.short_term else []
        
        # Get important items
        important = sorted(self.long_term, key=lambda x: x.importance, reverse=True)[:important_count]
        
        context = {
            "recent_memories": [item.to_dict() for item in recent],
            "important_memories": [item.to_dict() for item in important],
            "memory_stats": self.get_stats()
        }
        
        return context
    
    def forget(self, content_hash: str = None, item_type: str = None, 
               older_than: float = None) -> int:
        """
        Remove memory items based on criteria.
        
        Args:
            content_hash: Remove specific item by hash
            item_type: Remove all items of a specific type
            older_than: Remove items older than this timestamp
            
        Returns:
            Number of items removed
        """
        removed_count = 0
        
        if content_hash:
            # Remove specific item
            removed_count += self._remove_by_hash(content_hash)
        elif item_type:
            # Remove all items of specific type
            removed_count += self._remove_by_type(item_type)
        elif older_than:
            # Remove old items
            removed_count += self._remove_old_items(older_than)
        
        # Cleanup indexes
        self._cleanup_indexes()
        
        logger.info(f"Removed {removed_count} memory items")
        return removed_count
    
    def clear(self):
        """Clear all memory."""
        self.short_term.clear()
        self.long_term.clear()
        self.content_index.clear()
        self.type_index.clear()
        logger.info("Memory cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        return {
            "short_term_count": len(self.short_term),
            "long_term_count": len(self.long_term),
            "total_items": len(self.short_term) + len(self.long_term),
            "max_items": self.max_items,
            "ttl": self.ttl,
            "indexed_items": len(self.content_index),
            "type_distribution": {t: len(items) for t, items in self.type_index.items()}
        }
    
    def _store_in_short_term(self, item: MemoryItem, content_hash: str):
        """Store item in short-term memory."""
        self.short_term.append(item)
        self.content_index[content_hash] = item
    
    def _store_in_long_term(self, item: MemoryItem, content_hash: str):
        """Store item in long-term memory."""
        self.long_term.append(item)
        self.content_index[content_hash] = item
    
    def _update_indexes(self, item: MemoryItem, content_hash: str):
        """Update search indexes."""
        # Content index
        self.content_index[content_hash] = item
        
        # Type index
        if item.item_type not in self.type_index:
            self.type_index[item.item_type] = []
        self.type_index[item.item_type].append(item)
    
    def _hash_content(self, content: Any) -> str:
        """Generate a hash for content."""
        try:
            content_str = json.dumps(content, sort_keys=True, default=str)
            return str(hash(content_str))
        except:
            return str(hash(str(content)))
    
    def _filter_by_query(self, items: List[MemoryItem], query: str) -> List[MemoryItem]:
        """Filter items by text query."""
        query_lower = query.lower()
        filtered = []
        
        for item in items:
            # Search in content
            if isinstance(item.content, str) and query_lower in item.content.lower():
                filtered.append(item)
                continue
            
            # Search in metadata
            metadata_str = str(item.metadata).lower()
            if query_lower in metadata_str:
                filtered.append(item)
                continue
            
            # Search in item type
            if query_lower in item.item_type.lower():
                filtered.append(item)
        
        return filtered
    
    def _calculate_relevance(self, item: MemoryItem) -> float:
        """Calculate relevance score for sorting."""
        # Base relevance from importance
        relevance = item.importance
        
        # Recency bonus (items from last hour get bonus)
        age = time.time() - item.timestamp
        if age < 3600:  # 1 hour
            recency_bonus = 0.2 * (1 - age / 3600)
            relevance += recency_bonus
        
        # Access frequency bonus
        access_bonus = min(item.access_count * 0.1, 0.3)
        relevance += access_bonus
        
        return relevance
    
    def _remove_by_hash(self, content_hash: str) -> int:
        """Remove item by content hash."""
        if content_hash in self.content_index:
            item = self.content_index[content_hash]
            
            # Remove from appropriate memory tier
            if item in self.short_term:
                self.short_term.remove(item)
            elif item in self.long_term:
                self.long_term.remove(item)
            
            # Remove from indexes
            del self.content_index[content_hash]
            if item.item_type in self.type_index:
                self.type_index[item.item_type].remove(item)
            
            return 1
        return 0
    
    def _remove_by_type(self, item_type: str) -> int:
        """Remove all items of a specific type."""
        removed_count = 0
        
        if item_type in self.type_index:
            items_to_remove = self.type_index[item_type].copy()
            
            for item in items_to_remove:
                # Remove from memory tiers
                if item in self.short_term:
                    self.short_term.remove(item)
                elif item in self.long_term:
                    self.long_term.remove(item)
                
                # Remove from content index
                for hash_key, indexed_item in list(self.content_index.items()):
                    if indexed_item == item:
                        del self.content_index[hash_key]
                        break
                
                removed_count += 1
            
            # Clear type index
            del self.type_index[item_type]
        
        return removed_count
    
    def _remove_old_items(self, older_than: float) -> int:
        """Remove items older than specified timestamp."""
        removed_count = 0
        
        # Check short-term memory
        for item in list(self.short_term):
            if item.timestamp < older_than:
                self.short_term.remove(item)
                self._remove_from_indexes(item)
                removed_count += 1
        
        # Check long-term memory
        for item in list(self.long_term):
            if item.timestamp < older_than:
                self.long_term.remove(item)
                self._remove_from_indexes(item)
                removed_count += 1
        
        return removed_count
    
    def _remove_from_indexes(self, item: MemoryItem):
        """Remove item from all indexes."""
        # Remove from content index
        for hash_key, indexed_item in list(self.content_index.items()):
            if indexed_item == item:
                del self.content_index[hash_key]
                break
        
        # Remove from type index
        if item.item_type in self.type_index:
            if item in self.type_index[item.item_type]:
                self.type_index[item.item_type].remove(item)
    
    def _cleanup(self):
        """Perform memory cleanup operations."""
        current_time = time.time()
        
        # Remove expired items
        expired_items = []
        for item in list(self.short_term) + list(self.long_term):
            if current_time - item.timestamp > self.ttl:
                expired_items.append(item)
        
        for item in expired_items:
            self._remove_from_indexes(item)
            if item in self.short_term:
                self.short_term.remove(item)
            elif item in self.long_term:
                self.long_term.remove(item)
        
        if expired_items:
            logger.debug(f"Cleaned up {len(expired_items)} expired memory items")
    
    def _cleanup_indexes(self):
        """Clean up orphaned index entries."""
        # Remove orphaned content index entries
        orphaned_hashes = []
        for hash_key, item in self.content_index.items():
            if item not in self.short_term and item not in self.long_term:
                orphaned_hashes.append(hash_key)
        
        for hash_key in orphaned_hashes:
            del self.content_index[hash_key]
        
        # Remove orphaned type index entries
        for item_type in list(self.type_index.keys()):
            self.type_index[item_type] = [
                item for item in self.type_index[item_type]
                if item in self.short_term or item in self.long_term
            ]
            if not self.type_index[item_type]:
                del self.type_index[item_type]
        
        if orphaned_hashes:
            logger.debug(f"Cleaned up {len(orphaned_hashes)} orphaned index entries")
