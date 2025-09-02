"""
Search and retrieval tools for AI agents.
Provides functions for searching knowledge bases, code, and documents.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Union
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


def search_knowledge(query: str, knowledge_base: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Search through a knowledge base for relevant information.
    
    Args:
        query: Search query
        knowledge_base: List of knowledge items with 'title', 'content', 'tags' fields
        
    Returns:
        Dictionary containing search results and relevance scores
    """
    try:
        if not knowledge_base:
            return {"error": "Empty knowledge base"}
        
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for item in knowledge_base:
            score = _calculate_relevance_score(item, query_words, query_lower)
            
            if score > 0:
                results.append({
                    "item": item,
                    "score": score,
                    "matched_terms": _find_matched_terms(item, query_words)
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results),
            "top_results": results[:5] if results else []
        }
        
    except Exception as e:
        return {"error": f"Knowledge search failed: {str(e)}"}


def search_code(query: str, code_files: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Search through code files for relevant code snippets.
    
    Args:
        query: Search query
        code_files: List of code files with 'filename', 'content', 'language' fields
        
    Returns:
        Dictionary containing search results and code snippets
    """
    try:
        if not code_files:
            return {"error": "No code files provided"}
        
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for file_info in code_files:
            code_content = file_info.get("content", "")
            if not code_content:
                continue
            
            # Search for matches in code
            matches = _search_in_code(code_content, query_words, query_lower)
            
            if matches:
                results.append({
                    "filename": file_info.get("filename", "unknown"),
                    "language": file_info.get("language", "unknown"),
                    "matches": matches,
                    "total_matches": len(matches),
                    "relevance_score": _calculate_code_relevance(file_info, query_words)
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return {
            "query": query,
            "results": results,
            "total_files_with_matches": len(results),
            "total_matches": sum(r["total_matches"] for r in results)
        }
        
    except Exception as e:
        return {"error": f"Code search failed: {str(e)}"}


def search_documents(query: str, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Search through documents for relevant content.
    
    Args:
        query: Search query
        documents: List of documents with 'title', 'content', 'metadata' fields
        
    Returns:
        Dictionary containing search results and document excerpts
    """
    try:
        if not documents:
            return {"error": "No documents provided"}
        
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for doc in documents:
            content = doc.get("content", "")
            if not content:
                continue
            
            # Find relevant excerpts
            excerpts = _find_relevant_excerpts(content, query_words, query_lower)
            
            if excerpts:
                relevance_score = _calculate_document_relevance(doc, query_words)
                
                results.append({
                    "title": doc.get("title", "Untitled"),
                    "metadata": doc.get("metadata", {}),
                    "excerpts": excerpts,
                    "relevance_score": relevance_score,
                    "total_excerpts": len(excerpts)
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return {
            "query": query,
            "results": results,
            "total_documents": len(results),
            "top_results": results[:5] if results else []
        }
        
    except Exception as e:
        return {"error": f"Document search failed: {str(e)}"}


def semantic_search(query: str, items: List[Dict[str, Any]], 
                   similarity_threshold: float = 0.3) -> Dict[str, Any]:
    """
    Perform semantic search using similarity matching.
    
    Args:
        query: Search query
        items: List of items to search through
        similarity_threshold: Minimum similarity score to include in results
        
    Returns:
        Dictionary containing semantically similar results
    """
    try:
        if not items:
            return {"error": "No items provided"}
        
        results = []
        query_lower = query.lower()
        
        for item in items:
            # Calculate similarity with different fields
            title_similarity = _calculate_text_similarity(
                query_lower, 
                item.get("title", "").lower()
            )
            
            content_similarity = _calculate_text_similarity(
                query_lower, 
                item.get("content", "").lower()
            )
            
            tags_similarity = _calculate_text_similarity(
                query_lower, 
                " ".join(item.get("tags", [])).lower()
            )
            
            # Use the highest similarity score
            max_similarity = max(title_similarity, content_similarity, tags_similarity)
            
            if max_similarity >= similarity_threshold:
                results.append({
                    "item": item,
                    "similarity_score": max_similarity,
                    "title_similarity": title_similarity,
                    "content_similarity": content_similarity,
                    "tags_similarity": tags_similarity
                })
        
        # Sort by similarity score
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results),
            "similarity_threshold": similarity_threshold,
            "top_results": results[:5] if results else []
        }
        
    except Exception as e:
        return {"error": f"Semantic search failed: {str(e)}"}


def _calculate_relevance_score(item: Dict[str, Any], query_words: set, query_lower: str) -> float:
    """Calculate relevance score for a knowledge base item."""
    score = 0.0
    
    # Title relevance (highest weight)
    title = item.get("title", "").lower()
    if title:
        title_words = set(title.split())
        title_matches = len(query_words.intersection(title_words))
        score += title_matches * 3.0
        
        # Exact title match bonus
        if query_lower in title:
            score += 5.0
    
    # Content relevance
    content = item.get("content", "").lower()
    if content:
        content_words = set(content.split())
        content_matches = len(query_words.intersection(content_words))
        score += content_matches * 1.0
        
        # Exact phrase match bonus
        if query_lower in content:
            score += 3.0
    
    # Tags relevance
    tags = item.get("tags", [])
    for tag in tags:
        tag_lower = tag.lower()
        if any(word in tag_lower for word in query_words):
            score += 2.0
        if query_lower in tag_lower:
            score += 4.0
    
    # Recency bonus (if available)
    if "created_at" in item:
        # Simple recency bonus - could be more sophisticated
        score += 0.5
    
    return score


def _find_matched_terms(item: Dict[str, Any], query_words: set) -> List[str]:
    """Find which query terms matched in the item."""
    matched_terms = []
    
    title = item.get("title", "").lower()
    content = item.get("content", "").lower()
    tags = [tag.lower() for tag in item.get("tags", [])]
    
    for word in query_words:
        if (word in title or word in content or 
            any(word in tag for tag in tags)):
            matched_terms.append(word)
    
    return matched_terms


def _search_in_code(code_content: str, query_words: set, query_lower: str) -> List[Dict[str, Any]]:
    """Search for matches within code content."""
    matches = []
    lines = code_content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line_lower = line.lower()
        
        # Check for word matches
        word_matches = [word for word in query_words if word in line_lower]
        
        # Check for exact phrase match
        phrase_match = query_lower in line_lower
        
        if word_matches or phrase_match:
            # Find the context (surrounding lines)
            start_line = max(1, line_num - 2)
            end_line = min(len(lines), line_num + 2)
            
            context_lines = lines[start_line-1:end_line]
            context = '\n'.join(context_lines)
            
            matches.append({
                "line_number": line_num,
                "line_content": line.strip(),
                "context": context,
                "word_matches": word_matches,
                "phrase_match": phrase_match,
                "relevance": len(word_matches) + (2 if phrase_match else 0)
            })
    
    # Sort by relevance
    matches.sort(key=lambda x: x["relevance"], reverse=True)
    
    return matches


def _calculate_code_relevance(file_info: Dict[str, Any], query_words: set) -> float:
    """Calculate relevance score for a code file."""
    score = 0.0
    
    filename = file_info.get("filename", "").lower()
    language = file_info.get("language", "").lower()
    
    # Filename relevance
    for word in query_words:
        if word in filename:
            score += 2.0
    
    # Language relevance
    for word in query_words:
        if word in language:
            score += 1.0
    
    return score


def _find_relevant_excerpts(content: str, query_words: set, query_lower: str) -> List[Dict[str, Any]]:
    """Find relevant excerpts from document content."""
    excerpts = []
    sentences = re.split(r'[.!?]+', content)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        sentence_lower = sentence.lower()
        
        # Count word matches
        word_matches = [word for word in query_words if word in sentence_lower]
        
        # Check for exact phrase match
        phrase_match = query_lower in sentence_lower
        
        if word_matches or phrase_match:
            relevance = len(word_matches) + (3 if phrase_match else 0)
            
            excerpts.append({
                "text": sentence,
                "word_matches": word_matches,
                "phrase_match": phrase_match,
                "relevance": relevance
            })
    
    # Sort by relevance and take top excerpts
    excerpts.sort(key=lambda x: x["relevance"], reverse=True)
    return excerpts[:3]  # Return top 3 excerpts


def _calculate_document_relevance(doc: Dict[str, Any], query_words: set) -> float:
    """Calculate relevance score for a document."""
    score = 0.0
    
    title = doc.get("title", "").lower()
    content = doc.get("content", "").lower()
    
    # Title relevance
    for word in query_words:
        if word in title:
            score += 2.0
    
    # Content relevance
    for word in query_words:
        if word in content:
            score += 1.0
    
    # Metadata relevance
    metadata = doc.get("metadata", {})
    for key, value in metadata.items():
        if isinstance(value, str):
            value_lower = value.lower()
            for word in query_words:
                if word in value_lower:
                    score += 0.5
    
    return score


def _calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two text strings using SequenceMatcher."""
    if not text1 or not text2:
        return 0.0
    
    # Use SequenceMatcher for similarity
    similarity = SequenceMatcher(None, text1, text2).ratio()
    
    # Additional word overlap bonus
    words1 = set(text1.split())
    words2 = set(text2.split())
    
    if words1 and words2:
        overlap = len(words1.intersection(words2))
        total = len(words1.union(words2))
        word_similarity = overlap / total if total > 0 else 0.0
        
        # Combine sequence similarity with word overlap
        combined_similarity = (similarity + word_similarity) / 2
        return combined_similarity
    
    return similarity


def create_search_index(items: List[Dict[str, Any]], 
                       index_fields: List[str] = None) -> Dict[str, Any]:
    """
    Create a search index for faster searching.
    
    Args:
        items: List of items to index
        index_fields: Fields to include in the index
        
    Returns:
        Dictionary containing the search index
    """
    try:
        if not items:
            return {"error": "No items to index"}
        
        if index_fields is None:
            index_fields = ["title", "content", "tags"]
        
        # Create inverted index
        inverted_index = {}
        
        for item_id, item in enumerate(items):
            for field in index_fields:
                if field in item:
                    field_value = item[field]
                    
                    if isinstance(field_value, str):
                        words = field_value.lower().split()
                        for word in words:
                            if word not in inverted_index:
                                inverted_index[word] = []
                            inverted_index[word].append(item_id)
                    
                    elif isinstance(field_value, list):
                        for tag in field_value:
                            tag_lower = str(tag).lower()
                            if tag_lower not in inverted_index:
                                inverted_index[tag_lower] = []
                            inverted_index[tag_lower].append(item_id)
        
        # Create field weights for scoring
        field_weights = {
            "title": 3.0,
            "content": 1.0,
            "tags": 2.0
        }
        
        index_info = {
            "total_items": len(items),
            "indexed_fields": index_fields,
            "unique_terms": len(inverted_index),
            "field_weights": field_weights,
            "inverted_index": inverted_index
        }
        
        return index_info
        
    except Exception as e:
        return {"error": f"Index creation failed: {str(e)}"}


def search_with_index(query: str, search_index: Dict[str, Any], 
                     items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Search using a pre-built search index.
    
    Args:
        query: Search query
        search_index: Pre-built search index
        items: Original items list
        
    Returns:
        Dictionary containing search results
    """
    try:
        if "error" in search_index:
            return search_index
        
        query_words = set(query.lower().split())
        inverted_index = search_index.get("inverted_index", {})
        field_weights = search_index.get("field_weights", {})
        
        # Find matching items
        item_scores = {}
        
        for word in query_words:
            if word in inverted_index:
                for item_id in inverted_index[word]:
                    if item_id not in item_scores:
                        item_scores[item_id] = 0.0
                    
                    # Calculate score based on field weights
                    for field, weight in field_weights.items():
                        if field in items[item_id]:
                            field_value = items[item_id][field]
                            
                            if isinstance(field_value, str) and word in field_value.lower():
                                item_scores[item_id] += weight
                            elif isinstance(field_value, list):
                                for tag in field_value:
                                    if word in str(tag).lower():
                                        item_scores[item_id] += weight
        
        # Convert to results
        results = []
        for item_id, score in item_scores.items():
            if score > 0:
                results.append({
                    "item": items[item_id],
                    "score": score,
                    "item_id": item_id
                })
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results),
            "search_method": "indexed",
            "top_results": results[:5] if results else []
        }
        
    except Exception as e:
        return {"error": f"Indexed search failed: {str(e)}"}
