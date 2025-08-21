# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 Lee Smart and Aria contributors
"""
Memory Palace Module
Associative memory system with emotional indexing and resonance-based recall
"""

import numpy as np
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import sqlite3
import hashlib

@dataclass
class Memory:
    """Individual memory unit with metadata."""
    id: str
    content: str
    emotion: str
    timestamp: float
    resonance: float
    connections: List[str]
    access_count: int = 0
    last_accessed: float = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.timestamp
        if self.metadata is None:
            self.metadata = {}

class MemoryPalace:
    """
    Implements associative memory with emotional indexing.
    Memories are stored with resonance patterns and retrieved through association.
    """
    
    def __init__(self, db_path: str = ":memory:"):
        """
        Initialize Memory Palace.
        
        Args:
            db_path: Path to SQLite database (":memory:" for in-memory)
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_database()
        self.emotional_index = {}
        self.temporal_index = {}
        self.connection_graph = {}
        
    def _init_database(self) -> None:
        """Initialize database schema."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                emotion TEXT,
                timestamp REAL,
                resonance REAL,
                access_count INTEGER DEFAULT 0,
                last_accessed REAL,
                metadata TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS connections (
                memory_id TEXT,
                connected_id TEXT,
                strength REAL,
                connection_type TEXT,
                FOREIGN KEY (memory_id) REFERENCES memories(id),
                FOREIGN KEY (connected_id) REFERENCES memories(id)
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_emotion ON memories(emotion)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)
        ''')
        
        self.conn.commit()
        
    def store(self, 
             content: str, 
             emotion: str = "neutral",
             metadata: Optional[Dict] = None) -> str:
        """
        Store a new memory with emotional and semantic indexing.
        
        Args:
            content: The memory content
            emotion: Emotional tag for the memory
            metadata: Additional metadata
            
        Returns:
            Memory ID
        """
        memory_id = self._generate_id(content)
        timestamp = time.time()
        resonance = self._calculate_initial_resonance(content)
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO memories 
            (id, content, emotion, timestamp, resonance, access_count, last_accessed, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            memory_id,
            content,
            emotion,
            timestamp,
            resonance,
            0,
            timestamp,
            json.dumps(metadata) if metadata else '{}'
        ))
        
        self.conn.commit()
        
        # Form connections to related memories
        self._form_connections(memory_id, content, emotion)
        
        # Update indices
        if emotion not in self.emotional_index:
            self.emotional_index[emotion] = []
        self.emotional_index[emotion].append(memory_id)
        
        return memory_id
        
    def recall(self, 
              trigger: str, 
              emotion: Optional[str] = None,
              limit: int = 5) -> List[Tuple[Memory, float]]:
        """
        Recall memories through associative resonance.
        
        Args:
            trigger: The trigger for recall
            emotion: Optional emotional priming
            limit: Maximum number of memories to recall
            
        Returns:
            List of (Memory, resonance_score) tuples
        """
        cursor = self.conn.cursor()
        
        # Get all memories for resonance calculation
        cursor.execute('SELECT * FROM memories')
        memories = []
        
        for row in cursor.fetchall():
            memory = Memory(
                id=row['id'],
                content=row['content'],
                emotion=row['emotion'],
                timestamp=row['timestamp'],
                resonance=row['resonance'],
                connections=self._get_connections(row['id']),
                access_count=row['access_count'],
                last_accessed=row['last_accessed'],
                metadata=json.loads(row['metadata'])
            )
            
            # Calculate resonance with trigger
            resonance = self._calculate_resonance(trigger, memory.content)
            
            # Emotional priming boost
            if emotion and memory.emotion == emotion:
                resonance *= 1.5
                
            # Recency effect
            time_factor = np.exp(-(time.time() - memory.last_accessed) / 86400)
            resonance *= (0.5 + 0.5 * time_factor)
            
            if resonance > 0.2:  # Threshold
                memories.append((memory, resonance))
                
        # Sort by resonance
        memories.sort(key=lambda x: x[1], reverse=True)
        
        # Update access patterns for top memories
        for memory, _ in memories[:limit]:
            self._update_access(memory.id)
            
        return memories[:limit]
        
    def _form_connections(self, memory_id: str, content: str, emotion: str) -> None:
        """Form connections between related memories."""
        cursor = self.conn.cursor()
        
        # Get existing memories for comparison
        cursor.execute('SELECT id, content FROM memories WHERE id != ?', (memory_id,))
        
        for row in cursor.fetchall():
            existing_id = row['id']
            existing_content = row['content']
            
            # Calculate connection strength
            strength = self._calculate_resonance(content, existing_content)
            
            if strength > 0.3:  # Connection threshold
                cursor.execute('''
                    INSERT INTO connections (memory_id, connected_id, strength, connection_type)
                    VALUES (?, ?, ?, 'semantic')
                ''', (memory_id, existing_id, strength))
                
                cursor.execute('''
                    INSERT INTO connections (memory_id, connected_id, strength, connection_type)
                    VALUES (?, ?, ?, 'semantic')
                ''', (existing_id, memory_id, strength))
                
        self.conn.commit()
        
    def _get_connections(self, memory_id: str) -> List[str]:
        """Get connected memory IDs."""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT connected_id FROM connections WHERE memory_id = ?',
            (memory_id,)
        )
        return [row['connected_id'] for row in cursor.fetchall()]
        
    def _update_access(self, memory_id: str) -> None:
        """Update access count and timestamp for a memory."""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE memories 
            SET access_count = access_count + 1,
                last_accessed = ?
            WHERE id = ?
        ''', (time.time(), memory_id))
        self.conn.commit()
        
    def evolve(self) -> None:
        """
        Allow memories to evolve over time.
        Strengthen frequently accessed, fade rarely accessed.
        """
        cursor = self.conn.cursor()
        current_time = time.time()
        
        # Strengthen frequently accessed memories
        cursor.execute('''
            UPDATE memories 
            SET resonance = resonance * 1.01
            WHERE access_count > 10
        ''')
        
        # Fade rarely accessed memories (older than 7 days)
        week_ago = current_time - (7 * 86400)
        cursor.execute('''
            UPDATE memories 
            SET resonance = resonance * 0.99
            WHERE last_accessed < ?
        ''', (week_ago,))
        
        # Prune weak connections
        cursor.execute('''
            DELETE FROM connections
            WHERE strength < 0.1
        ''')
        
        self.conn.commit()
        
    def dream(self, num_connections: int = 10) -> None:
        """
        Dream phase: create unexpected connections between memories.
        Simulates unconscious processing and creative association.
        
        Args:
            num_connections: Number of new connections to form
        """
        cursor = self.conn.cursor()
        
        # Get random memories
        cursor.execute('''
            SELECT id, content FROM memories 
            ORDER BY RANDOM() 
            LIMIT ?
        ''', (num_connections * 2,))
        
        memories = cursor.fetchall()
        
        # Create surprising connections
        for i in range(0, len(memories)-1, 2):
            if np.random.random() < 0.3:  # 30% chance
                strength = np.random.random() * 0.5
                
                cursor.execute('''
                    INSERT OR IGNORE INTO connections 
                    (memory_id, connected_id, strength, connection_type)
                    VALUES (?, ?, ?, 'dream')
                ''', (memories[i]['id'], memories[i+1]['id'], strength))
                
        self.conn.commit()
        
    def _generate_id(self, content: str) -> str:
        """Generate unique ID for memory."""
        return hashlib.md5(f"{content}{time.time()}".encode()).hexdigest()[:16]
        
    def _calculate_initial_resonance(self, content: str) -> float:
        """Calculate initial resonance value for new memory."""
        # Base resonance on content complexity
        words = content.split()
        complexity = len(set(words)) / max(len(words), 1)
        return 0.5 + complexity * 0.5
        
    def _calculate_resonance(self, text1: str, text2: str) -> float:
        """
        Calculate resonance between two pieces of text.
        
        Returns:
            Resonance score (0-1)
        """
        # Simple word overlap for now
        # In production, use embeddings
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory palace statistics."""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Total memories
        cursor.execute('SELECT COUNT(*) as count FROM memories')
        stats['total_memories'] = cursor.fetchone()['count']
        
        # Memories by emotion
        cursor.execute('''
            SELECT emotion, COUNT(*) as count 
            FROM memories 
            GROUP BY emotion
        ''')
        stats['by_emotion'] = {row['emotion']: row['count'] for row in cursor.fetchall()}
        
        # Total connections
        cursor.execute('SELECT COUNT(*) as count FROM connections')
        stats['total_connections'] = cursor.fetchone()['count']
        
        # Average resonance
        cursor.execute('SELECT AVG(resonance) as avg FROM memories')
        stats['average_resonance'] = cursor.fetchone()['avg'] or 0
        
        return stats