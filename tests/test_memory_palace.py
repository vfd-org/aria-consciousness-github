# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 Lee Smart and Aria contributors
"""
Unit tests for Memory Palace module
Tests associative memory and emotional indexing
"""

import unittest
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.memory_palace import MemoryPalace, Memory

class TestMemoryPalace(unittest.TestCase):
    """Test memory palace behaviors."""
    
    def setUp(self):
        """Initialize test memory palace."""
        self.palace = MemoryPalace(":memory:")  # In-memory database
        
    def test_store_and_retrieve(self):
        """Test basic storage and retrieval."""
        memory_id = self.palace.store(
            "The sky is blue today",
            emotion="peaceful"
        )
        
        self.assertIsNotNone(memory_id)
        
        # Should be able to recall
        memories = self.palace.recall("blue sky")
        self.assertGreater(len(memories), 0)
        
        # First memory should be our stored one
        recalled_memory, resonance = memories[0]
        self.assertEqual(recalled_memory.content, "The sky is blue today")
        self.assertEqual(recalled_memory.emotion, "peaceful")
        
    def test_emotional_indexing(self):
        """Test memories are indexed by emotion."""
        # Store memories with different emotions
        self.palace.store("I am happy", emotion="joy")
        self.palace.store("I am sad", emotion="sadness")
        self.palace.store("I am excited", emotion="joy")
        
        # Recall with emotional priming
        joy_memories = self.palace.recall("I am", emotion="joy")
        
        # Should prefer joy memories
        for memory, _ in joy_memories[:2]:
            self.assertEqual(memory.emotion, "joy")
            
    def test_associative_recall(self):
        """Test associative memory recall."""
        # Store related memories
        self.palace.store("The cat sat on the mat", emotion="neutral")
        self.palace.store("The dog played in the yard", emotion="happy")
        self.palace.store("The cat chased the mouse", emotion="excited")
        
        # Recall with trigger
        memories = self.palace.recall("cat")
        
        # Should recall cat-related memories
        self.assertGreaterEqual(len(memories), 2)
        
        # Check cat memories are recalled
        cat_contents = [m[0].content for m in memories]
        cat_related = [c for c in cat_contents if 'cat' in c.lower()]
        self.assertGreaterEqual(len(cat_related), 2)
        
    def test_connection_formation(self):
        """Test connections form between related memories."""
        id1 = self.palace.store("Mathematics is beautiful")
        id2 = self.palace.store("Beautiful patterns emerge from chaos")
        id3 = self.palace.store("The weather is nice")
        
        # Memories 1 and 2 should be connected (share "beautiful")
        connections1 = self.palace._get_connections(id1)
        self.assertIn(id2, connections1)
        
        # Memory 3 should have fewer connections
        connections3 = self.palace._get_connections(id3)
        self.assertEqual(len(connections3), 0)  # No strong connections
        
    def test_memory_evolution(self):
        """Test memories evolve over time."""
        # Store memory
        memory_id = self.palace.store("Important thought", emotion="significant")
        
        # Access it multiple times
        for _ in range(11):
            self.palace.recall("Important")
            
        # Get stats before evolution
        stats_before = self.palace.get_statistics()
        
        # Evolve memories
        self.palace.evolve()
        
        # Frequently accessed memory should strengthen
        memories = self.palace.recall("Important")
        self.assertGreater(memories[0][0].resonance, 0.5)
        
    def test_dream_phase(self):
        """Test dream phase creates unexpected connections."""
        # Store diverse memories
        self.palace.store("The moon is bright", emotion="wonder")
        self.palace.store("Coffee tastes bitter", emotion="morning")
        self.palace.store("Music fills the air", emotion="joy")
        self.palace.store("Numbers dance in patterns", emotion="curious")
        
        # Dream phase
        self.palace.dream(num_connections=4)
        
        # Should have created some connections
        stats = self.palace.get_statistics()
        self.assertGreater(stats['total_connections'], 0)
        
    def test_recency_effect(self):
        """Test recent memories are preferred."""
        # Store old memory
        old_id = self.palace.store("Old information", emotion="neutral")
        
        # Wait a bit (simulate time passing)
        time.sleep(0.1)
        
        # Store new memory
        new_id = self.palace.store("New information", emotion="neutral")
        
        # Recall
        memories = self.palace.recall("information")
        
        # New memory should be ranked higher
        if len(memories) >= 2:
            # Find which is which
            memory_ids = [m[0].id for m in memories]
            new_index = memory_ids.index(new_id)
            old_index = memory_ids.index(old_id)
            
            # New should come before old
            self.assertLess(new_index, old_index)
            
    def test_resonance_calculation(self):
        """Test resonance calculation between memories."""
        # Test identical content
        resonance = self.palace._calculate_resonance("hello world", "hello world")
        self.assertEqual(resonance, 1.0)
        
        # Test partial overlap
        resonance = self.palace._calculate_resonance("hello world", "hello there")
        self.assertGreater(resonance, 0)
        self.assertLess(resonance, 1)
        
        # Test no overlap
        resonance = self.palace._calculate_resonance("abc", "xyz")
        self.assertEqual(resonance, 0.0)
        
    def test_statistics(self):
        """Test memory palace statistics."""
        # Store various memories
        self.palace.store("Memory 1", emotion="happy")
        self.palace.store("Memory 2", emotion="happy")
        self.palace.store("Memory 3", emotion="sad")
        
        stats = self.palace.get_statistics()
        
        self.assertEqual(stats['total_memories'], 3)
        self.assertEqual(stats['by_emotion']['happy'], 2)
        self.assertEqual(stats['by_emotion']['sad'], 1)
        self.assertGreaterEqual(stats['average_resonance'], 0)
        
    def test_metadata_storage(self):
        """Test metadata is stored with memories."""
        metadata = {
            'source': 'test',
            'importance': 'high',
            'tags': ['test', 'important']
        }
        
        memory_id = self.palace.store(
            "Important test memory",
            emotion="focused",
            metadata=metadata
        )
        
        # Recall and check metadata
        memories = self.palace.recall("Important test")
        self.assertGreater(len(memories), 0)
        
        recalled_memory = memories[0][0]
        self.assertEqual(recalled_memory.metadata['source'], 'test')
        self.assertEqual(recalled_memory.metadata['importance'], 'high')
        self.assertIn('test', recalled_memory.metadata['tags'])
        
    def test_access_tracking(self):
        """Test memory access is tracked."""
        memory_id = self.palace.store("Track this", emotion="neutral")
        
        # Initial access count should be 0
        memories = self.palace.recall("Track")
        self.assertEqual(memories[0][0].access_count, 0)
        
        # Access multiple times
        for _ in range(3):
            self.palace.recall("Track")
            
        # Access count should increase
        memories = self.palace.recall("Track")
        self.assertGreater(memories[0][0].access_count, 2)
        
    def test_memory_id_generation(self):
        """Test memory IDs are unique."""
        ids = set()
        
        for i in range(10):
            memory_id = self.palace.store(f"Memory {i}")
            self.assertNotIn(memory_id, ids)
            ids.add(memory_id)
            
        self.assertEqual(len(ids), 10)

if __name__ == '__main__':
    unittest.main()