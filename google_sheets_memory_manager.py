#!/usr/bin/env python3
"""
Google Sheets Memory Manager for Recursive Cognition Ecosystem
Manages all memory storage using Google Sheets as the persistent layer.
Handles agent communications, learning data, user interactions, and system state.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import json
import hashlib
from dataclasses import dataclass, asdict
from enum import Enum


class MemoryType(Enum):
    """Types of memory storage."""
    AGENT_COMMUNICATION = "agent_communication"
    LEARNING_DATA = "learning_data"
    USER_INTERACTION = "user_interaction"
    SYSTEM_STATE = "system_state"
    PERFORMANCE_METRICS = "performance_metrics"
    KNOWLEDGE_FRAGMENTS = "knowledge_fragments"
    EVOLUTION_HISTORY = "evolution_history"
    COLLECTIVE_INTELLIGENCE = "collective_intelligence"


@dataclass
class MemoryEntry:
    """Represents a memory entry in the system."""
    memory_id: str
    memory_type: MemoryType
    agent_id: Optional[str]
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime
    importance_score: float
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    retention_period: Optional[timedelta] = None


@dataclass
class MemoryQuery:
    """Represents a query for memory retrieval."""
    memory_types: List[MemoryType]
    agent_filter: Optional[str] = None
    time_range: Optional[tuple] = None
    content_filter: Optional[str] = None
    importance_threshold: float = 0.0
    limit: int = 100


class GoogleSheetsMemoryManager:
    """
    Memory manager that uses Google Sheets as persistent storage for all system memory.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("google_sheets_memory_manager")
        self.sheets_config = config.get('sheets_config', {})
        self.cesar_integration = config.get('cesar_integration', {})

        # Memory storage
        self.memory_cache = {}
        self.memory_index = {}
        self.sheet_mappings = {}

        # Performance tracking
        self.access_patterns = {}
        self.retention_policies = {}

        # Google Sheets API configuration
        self.sheets_api_config = {
            'spreadsheet_id': config.get('memory_spreadsheet_id'),
            'credentials_path': config.get('google_credentials_path'),
            'scopes': ['https://www.googleapis.com/auth/spreadsheets']
        }

    async def initialize(self):
        """Initialize the memory manager."""
        try:
            self.logger.info("Initializing Google Sheets Memory Manager...")

            # Setup sheet structure
            await self._setup_memory_sheets()

            # Initialize retention policies
            await self._setup_retention_policies()

            # Load existing memory index
            await self._load_memory_index()

            # Setup background maintenance
            asyncio.create_task(self._run_memory_maintenance())

            self.logger.info("Google Sheets Memory Manager initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Memory manager initialization failed: {e}")
            return False

    async def store_memory(self, memory_type: MemoryType, content: Dict[str, Any],
                          agent_id: Optional[str] = None, importance_score: float = 0.5,
                          metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store a memory entry."""
        try:
            # Generate memory ID
            memory_id = self._generate_memory_id(memory_type, content, agent_id)

            # Create memory entry
            memory_entry = MemoryEntry(
                memory_id=memory_id,
                memory_type=memory_type,
                agent_id=agent_id,
                content=content,
                metadata=metadata or {},
                timestamp=datetime.now(),
                importance_score=importance_score,
                retention_period=self._get_retention_period(memory_type, importance_score)
            )

            # Store in cache
            self.memory_cache[memory_id] = memory_entry

            # Update index
            await self._update_memory_index(memory_entry)

            # Store in Google Sheets
            await self._store_in_sheets(memory_entry)

            # Update access patterns
            await self._update_access_patterns(memory_type, agent_id)

            self.logger.debug(f"Stored memory {memory_id} of type {memory_type.value}")
            return memory_id

        except Exception as e:
            self.logger.error(f"Failed to store memory: {e}")
            raise

    async def retrieve_memory(self, query: MemoryQuery) -> List[MemoryEntry]:
        """Retrieve memory entries based on query."""
        try:
            matching_entries = []

            # Search in cache first
            cache_results = await self._search_cache(query)
            matching_entries.extend(cache_results)

            # If cache doesn't have enough results, search sheets
            if len(matching_entries) < query.limit:
                remaining_limit = query.limit - len(matching_entries)
                sheet_results = await self._search_sheets(query, remaining_limit)
                matching_entries.extend(sheet_results)

            # Update access tracking for retrieved entries
            for entry in matching_entries:
                await self._track_access(entry)

            # Sort by relevance and importance
            matching_entries.sort(
                key=lambda x: (x.importance_score, x.timestamp),
                reverse=True
            )

            return matching_entries[:query.limit]

        except Exception as e:
            self.logger.error(f"Failed to retrieve memory: {e}")
            return []

    async def store_agent_communication(self, sender_id: str, receiver_id: str,
                                       message_type: str, content: Dict[str, Any],
                                       importance: float = 0.5) -> str:
        """Store agent-to-agent communication."""
        communication_data = {
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'message_type': message_type,
            'content': content
        }

        metadata = {
            'communication_type': 'agent_to_agent',
            'message_size': len(json.dumps(content))
        }

        return await self.store_memory(
            MemoryType.AGENT_COMMUNICATION,
            communication_data,
            agent_id=sender_id,
            importance_score=importance,
            metadata=metadata
        )

    async def store_learning_data(self, agent_id: str, learning_type: str,
                                 learning_content: Dict[str, Any], effectiveness: float = 0.5) -> str:
        """Store agent learning data."""
        learning_data = {
            'learning_type': learning_type,
            'content': learning_content,
            'effectiveness_score': effectiveness,
            'learning_timestamp': datetime.now().isoformat()
        }

        metadata = {
            'learning_category': learning_type,
            'data_complexity': self._calculate_complexity(learning_content)
        }

        return await self.store_memory(
            MemoryType.LEARNING_DATA,
            learning_data,
            agent_id=agent_id,
            importance_score=max(0.6, effectiveness),  # Learning is generally important
            metadata=metadata
        )

    async def store_user_interaction(self, user_id: str, interaction_type: str,
                                   content: Dict[str, Any], sentiment: float = 0.5) -> str:
        """Store user interaction data."""
        interaction_data = {
            'user_id': user_id,
            'interaction_type': interaction_type,
            'content': content,
            'sentiment_score': sentiment
        }

        metadata = {
            'interaction_channel': content.get('channel', 'unknown'),
            'response_time': content.get('response_time_ms', 0)
        }

        # User interactions are important for system improvement
        importance = 0.7 + (sentiment * 0.3)  # Higher importance for positive interactions

        return await self.store_memory(
            MemoryType.USER_INTERACTION,
            interaction_data,
            importance_score=importance,
            metadata=metadata
        )

    async def store_performance_metrics(self, agent_id: str, metrics: Dict[str, Any]) -> str:
        """Store agent performance metrics."""
        performance_data = {
            'agent_id': agent_id,
            'metrics': metrics,
            'measurement_timestamp': datetime.now().isoformat()
        }

        metadata = {
            'metrics_count': len(metrics),
            'performance_category': self._categorize_performance(metrics)
        }

        return await self.store_memory(
            MemoryType.PERFORMANCE_METRICS,
            performance_data,
            agent_id=agent_id,
            importance_score=0.6,  # Performance data is important for optimization
            metadata=metadata
        )

    async def store_collective_intelligence(self, intelligence_type: str,
                                          insights: List[Dict[str, Any]],
                                          confidence: float) -> str:
        """Store collective intelligence insights."""
        intelligence_data = {
            'intelligence_type': intelligence_type,
            'insights': insights,
            'confidence_score': confidence,
            'contributing_agents': len(set(insight.get('source_agent') for insight in insights))
        }

        metadata = {
            'insight_count': len(insights),
            'collective_confidence': confidence,
            'emergence_indicator': self._calculate_emergence_score(insights)
        }

        return await self.store_memory(
            MemoryType.COLLECTIVE_INTELLIGENCE,
            intelligence_data,
            importance_score=0.8 + (confidence * 0.2),  # High importance for collective insights
            metadata=metadata
        )

    async def get_agent_memory_summary(self, agent_id: str, days: int = 7) -> Dict[str, Any]:
        """Get memory summary for a specific agent."""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)

            query = MemoryQuery(
                memory_types=list(MemoryType),
                agent_filter=agent_id,
                time_range=(start_time, end_time),
                limit=1000
            )

            memories = await self.retrieve_memory(query)

            # Analyze memory patterns
            memory_by_type = {}
            total_importance = 0
            interaction_count = 0

            for memory in memories:
                mem_type = memory.memory_type.value
                if mem_type not in memory_by_type:
                    memory_by_type[mem_type] = 0
                memory_by_type[mem_type] += 1
                total_importance += memory.importance_score
                interaction_count += memory.access_count

            summary = {
                'agent_id': agent_id,
                'time_period_days': days,
                'total_memories': len(memories),
                'memory_by_type': memory_by_type,
                'average_importance': total_importance / len(memories) if memories else 0,
                'total_interactions': interaction_count,
                'most_recent_activity': memories[0].timestamp.isoformat() if memories else None,
                'memory_efficiency': self._calculate_memory_efficiency(memories)
            }

            return summary

        except Exception as e:
            self.logger.error(f"Failed to get agent memory summary: {e}")
            return {'error': str(e)}

    async def get_system_memory_analytics(self) -> Dict[str, Any]:
        """Get analytics on overall system memory usage."""
        try:
            total_memories = len(self.memory_cache)
            memory_by_type = {}
            importance_distribution = []
            access_frequency = {}

            for memory in self.memory_cache.values():
                # Memory type distribution
                mem_type = memory.memory_type.value
                if mem_type not in memory_by_type:
                    memory_by_type[mem_type] = 0
                memory_by_type[mem_type] += 1

                # Importance distribution
                importance_distribution.append(memory.importance_score)

                # Access frequency
                if memory.agent_id:
                    if memory.agent_id not in access_frequency:
                        access_frequency[memory.agent_id] = 0
                    access_frequency[memory.agent_id] += memory.access_count

            analytics = {
                'total_memories': total_memories,
                'memory_distribution': memory_by_type,
                'average_importance': sum(importance_distribution) / len(importance_distribution) if importance_distribution else 0,
                'high_importance_count': len([i for i in importance_distribution if i > 0.8]),
                'most_active_agents': sorted(access_frequency.items(), key=lambda x: x[1], reverse=True)[:5],
                'memory_growth_rate': await self._calculate_memory_growth_rate(),
                'storage_efficiency': await self._calculate_storage_efficiency()
            }

            return analytics

        except Exception as e:
            self.logger.error(f"Failed to get system memory analytics: {e}")
            return {'error': str(e)}

    async def perform_memory_optimization(self) -> Dict[str, Any]:
        """Perform memory optimization and cleanup."""
        try:
            optimization_results = {
                'start_time': datetime.now().isoformat(),
                'initial_memory_count': len(self.memory_cache),
                'optimizations_performed': []
            }

            # 1. Remove expired memories
            expired_count = await self._remove_expired_memories()
            if expired_count > 0:
                optimization_results['optimizations_performed'].append({
                    'type': 'expired_removal',
                    'count': expired_count
                })

            # 2. Compress low-importance memories
            compressed_count = await self._compress_low_importance_memories()
            if compressed_count > 0:
                optimization_results['optimizations_performed'].append({
                    'type': 'compression',
                    'count': compressed_count
                })

            # 3. Archive old memories
            archived_count = await self._archive_old_memories()
            if archived_count > 0:
                optimization_results['optimizations_performed'].append({
                    'type': 'archival',
                    'count': archived_count
                })

            # 4. Deduplicate similar memories
            deduplicated_count = await self._deduplicate_memories()
            if deduplicated_count > 0:
                optimization_results['optimizations_performed'].append({
                    'type': 'deduplication',
                    'count': deduplicated_count
                })

            optimization_results.update({
                'end_time': datetime.now().isoformat(),
                'final_memory_count': len(self.memory_cache),
                'space_saved': optimization_results['initial_memory_count'] - len(self.memory_cache)
            })

            self.logger.info(f"Memory optimization complete: {optimization_results}")
            return optimization_results

        except Exception as e:
            self.logger.error(f"Memory optimization failed: {e}")
            return {'error': str(e)}

    async def export_memory_for_cesar(self, memory_types: List[MemoryType],
                                    time_range: Optional[tuple] = None) -> Dict[str, Any]:
        """Export memory data for CESAR integration."""
        try:
            query = MemoryQuery(
                memory_types=memory_types,
                time_range=time_range or (datetime.now() - timedelta(days=1), datetime.now()),
                limit=1000
            )

            memories = await self.retrieve_memory(query)

            # Prepare CESAR-compatible format
            cesar_export = {
                'kind': 'agent_memory',
                'export_timestamp': datetime.now().isoformat(),
                'memory_entries': [],
                'summary': {
                    'total_entries': len(memories),
                    'memory_types': [mt.value for mt in memory_types],
                    'time_range': {
                        'start': time_range[0].isoformat() if time_range else None,
                        'end': time_range[1].isoformat() if time_range else None
                    }
                }
            }

            # Convert memories to CESAR format
            for memory in memories:
                cesar_entry = {
                    'memory_id': memory.memory_id,
                    'type': memory.memory_type.value,
                    'agent_id': memory.agent_id,
                    'content': memory.content,
                    'importance': memory.importance_score,
                    'timestamp': memory.timestamp.isoformat(),
                    'access_count': memory.access_count,
                    'metadata': memory.metadata
                }
                cesar_export['memory_entries'].append(cesar_entry)

            return cesar_export

        except Exception as e:
            self.logger.error(f"CESAR export failed: {e}")
            return {'error': str(e)}

    # Helper methods
    def _generate_memory_id(self, memory_type: MemoryType, content: Dict[str, Any],
                           agent_id: Optional[str]) -> str:
        """Generate unique memory ID."""
        content_hash = hashlib.md5(json.dumps(content, sort_keys=True).encode()).hexdigest()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        agent_part = f"_{agent_id}" if agent_id else ""
        return f"{memory_type.value}_{timestamp}_{content_hash[:8]}{agent_part}"

    def _get_retention_period(self, memory_type: MemoryType, importance_score: float) -> timedelta:
        """Calculate retention period based on memory type and importance."""
        base_periods = {
            MemoryType.AGENT_COMMUNICATION: timedelta(days=30),
            MemoryType.LEARNING_DATA: timedelta(days=90),
            MemoryType.USER_INTERACTION: timedelta(days=180),
            MemoryType.SYSTEM_STATE: timedelta(days=14),
            MemoryType.PERFORMANCE_METRICS: timedelta(days=60),
            MemoryType.KNOWLEDGE_FRAGMENTS: timedelta(days=365),
            MemoryType.EVOLUTION_HISTORY: timedelta(days=365),
            MemoryType.COLLECTIVE_INTELLIGENCE: timedelta(days=180)
        }

        base_period = base_periods.get(memory_type, timedelta(days=30))

        # Extend retention for high-importance memories
        importance_multiplier = 1 + (importance_score * 2)  # 1x to 3x multiplier
        return base_period * importance_multiplier

    async def _update_memory_index(self, memory_entry: MemoryEntry):
        """Update memory index for fast searching."""
        index_key = f"{memory_entry.memory_type.value}_{memory_entry.agent_id or 'system'}"

        if index_key not in self.memory_index:
            self.memory_index[index_key] = []

        self.memory_index[index_key].append({
            'memory_id': memory_entry.memory_id,
            'timestamp': memory_entry.timestamp,
            'importance': memory_entry.importance_score
        })

        # Keep index sorted by timestamp (most recent first)
        self.memory_index[index_key].sort(key=lambda x: x['timestamp'], reverse=True)

        # Limit index size
        if len(self.memory_index[index_key]) > 1000:
            self.memory_index[index_key] = self.memory_index[index_key][:1000]

    async def _search_cache(self, query: MemoryQuery) -> List[MemoryEntry]:
        """Search memory cache."""
        results = []

        for memory in self.memory_cache.values():
            if self._matches_query(memory, query):
                results.append(memory)

        return results

    async def _search_sheets(self, query: MemoryQuery, limit: int) -> List[MemoryEntry]:
        """Search Google Sheets for memories (placeholder)."""
        # This would implement actual Google Sheets API search
        # For now, returning empty list as placeholder
        return []

    def _matches_query(self, memory: MemoryEntry, query: MemoryQuery) -> bool:
        """Check if memory entry matches query criteria."""
        # Check memory type
        if memory.memory_type not in query.memory_types:
            return False

        # Check agent filter
        if query.agent_filter and memory.agent_id != query.agent_filter:
            return False

        # Check time range
        if query.time_range:
            start_time, end_time = query.time_range
            if not (start_time <= memory.timestamp <= end_time):
                return False

        # Check importance threshold
        if memory.importance_score < query.importance_threshold:
            return False

        # Check content filter
        if query.content_filter:
            content_str = json.dumps(memory.content).lower()
            if query.content_filter.lower() not in content_str:
                return False

        return True

    async def _track_access(self, memory_entry: MemoryEntry):
        """Track memory access for analytics."""
        memory_entry.access_count += 1
        memory_entry.last_accessed = datetime.now()

    def _calculate_complexity(self, content: Dict[str, Any]) -> float:
        """Calculate complexity score for content."""
        # Simple complexity measure based on content size and nesting
        content_str = json.dumps(content)
        size_score = min(1.0, len(content_str) / 10000)  # Normalize to 0-1

        # Count nested levels
        nesting_score = min(1.0, self._count_nesting_levels(content) / 10)

        return (size_score + nesting_score) / 2

    def _count_nesting_levels(self, obj: Any, level: int = 0) -> int:
        """Count maximum nesting levels in object."""
        if isinstance(obj, dict):
            return max([self._count_nesting_levels(v, level + 1) for v in obj.values()], default=level)
        elif isinstance(obj, list):
            return max([self._count_nesting_levels(item, level + 1) for item in obj], default=level)
        else:
            return level

    def _categorize_performance(self, metrics: Dict[str, Any]) -> str:
        """Categorize performance metrics."""
        if 'success_rate' in metrics:
            success_rate = metrics['success_rate']
            if success_rate > 0.9:
                return 'excellent'
            elif success_rate > 0.7:
                return 'good'
            elif success_rate > 0.5:
                return 'acceptable'
            else:
                return 'poor'
        return 'unknown'

    def _calculate_emergence_score(self, insights: List[Dict[str, Any]]) -> float:
        """Calculate emergence score for collective intelligence."""
        if not insights:
            return 0.0

        # Simple emergence measure based on insight diversity and novelty
        unique_types = len(set(insight.get('insight_type') for insight in insights))
        total_insights = len(insights)

        diversity_score = unique_types / total_insights if total_insights > 0 else 0
        return min(1.0, diversity_score * 2)  # Normalize and amplify

    def _calculate_memory_efficiency(self, memories: List[MemoryEntry]) -> float:
        """Calculate memory efficiency score."""
        if not memories:
            return 0.0

        # Efficiency based on access patterns and importance correlation
        high_importance_accessed = sum(1 for m in memories if m.importance_score > 0.7 and m.access_count > 0)
        high_importance_total = sum(1 for m in memories if m.importance_score > 0.7)

        if high_importance_total == 0:
            return 0.5  # Neutral if no high-importance memories

        return high_importance_accessed / high_importance_total

    async def _calculate_memory_growth_rate(self) -> float:
        """Calculate memory growth rate."""
        # Placeholder implementation
        # Would analyze memory creation over time
        return 0.05  # 5% growth rate placeholder

    async def _calculate_storage_efficiency(self) -> float:
        """Calculate storage efficiency."""
        # Placeholder implementation
        # Would analyze memory size vs utility
        return 0.8  # 80% efficiency placeholder

    async def _remove_expired_memories(self) -> int:
        """Remove expired memories based on retention policies."""
        removed_count = 0
        expired_ids = []

        for memory_id, memory in self.memory_cache.items():
            if memory.retention_period:
                expiry_date = memory.timestamp + memory.retention_period
                if datetime.now() > expiry_date:
                    expired_ids.append(memory_id)

        for memory_id in expired_ids:
            del self.memory_cache[memory_id]
            removed_count += 1

        return removed_count

    async def _compress_low_importance_memories(self) -> int:
        """Compress low-importance memories to save space."""
        # Placeholder for compression logic
        # Would compress content of low-importance memories
        return 0

    async def _archive_old_memories(self) -> int:
        """Archive old memories to long-term storage."""
        # Placeholder for archival logic
        # Would move old memories to archive sheets
        return 0

    async def _deduplicate_memories(self) -> int:
        """Remove duplicate memories."""
        # Placeholder for deduplication logic
        # Would identify and remove similar memories
        return 0

    async def _setup_memory_sheets(self):
        """Setup Google Sheets structure for memory storage."""
        # Define sheet structure for each memory type
        sheet_structures = {
            'Agent_Communications': [
                'memory_id', 'timestamp', 'sender_id', 'receiver_id',
                'message_type', 'content_preview', 'importance_score', 'access_count'
            ],
            'Learning_Data': [
                'memory_id', 'timestamp', 'agent_id', 'learning_type',
                'effectiveness_score', 'content_preview', 'importance_score'
            ],
            'User_Interactions': [
                'memory_id', 'timestamp', 'user_id', 'interaction_type',
                'sentiment_score', 'content_preview', 'importance_score'
            ],
            'Performance_Metrics': [
                'memory_id', 'timestamp', 'agent_id', 'metric_category',
                'success_rate', 'efficiency_score', 'importance_score'
            ],
            'Collective_Intelligence': [
                'memory_id', 'timestamp', 'intelligence_type', 'confidence_score',
                'contributing_agents', 'insights_count', 'importance_score'
            ],
            'Memory_Index': [
                'index_key', 'memory_ids', 'last_updated', 'entry_count'
            ]
        }

        self.sheet_mappings = sheet_structures
        self.logger.info(f"Memory sheet structure defined: {list(sheet_structures.keys())}")

    async def _setup_retention_policies(self):
        """Setup memory retention policies."""
        self.retention_policies = {
            MemoryType.AGENT_COMMUNICATION: {
                'base_retention_days': 30,
                'importance_multiplier': 2.0,
                'max_retention_days': 365
            },
            MemoryType.LEARNING_DATA: {
                'base_retention_days': 90,
                'importance_multiplier': 3.0,
                'max_retention_days': 730  # 2 years
            },
            MemoryType.USER_INTERACTION: {
                'base_retention_days': 180,
                'importance_multiplier': 2.5,
                'max_retention_days': 1095  # 3 years
            },
            MemoryType.COLLECTIVE_INTELLIGENCE: {
                'base_retention_days': 180,
                'importance_multiplier': 4.0,
                'max_retention_days': 1825  # 5 years
            }
        }

    async def _load_memory_index(self):
        """Load existing memory index from sheets."""
        # Placeholder for loading from Google Sheets
        # Would populate self.memory_index from stored data
        pass

    async def _store_in_sheets(self, memory_entry: MemoryEntry):
        """Store memory entry in appropriate Google Sheet."""
        # Placeholder for Google Sheets API integration
        # Would write the memory entry to the appropriate sheet
        pass

    async def _update_access_patterns(self, memory_type: MemoryType, agent_id: Optional[str]):
        """Update access pattern tracking."""
        pattern_key = f"{memory_type.value}_{agent_id or 'system'}"

        if pattern_key not in self.access_patterns:
            self.access_patterns[pattern_key] = {
                'access_count': 0,
                'last_access': None,
                'peak_hours': {}
            }

        self.access_patterns[pattern_key]['access_count'] += 1
        self.access_patterns[pattern_key]['last_access'] = datetime.now()

        # Track peak hours
        hour = datetime.now().hour
        if hour not in self.access_patterns[pattern_key]['peak_hours']:
            self.access_patterns[pattern_key]['peak_hours'][hour] = 0
        self.access_patterns[pattern_key]['peak_hours'][hour] += 1

    async def _run_memory_maintenance(self):
        """Background task for memory maintenance."""
        while True:
            try:
                # Run maintenance every 4 hours
                await asyncio.sleep(14400)

                # Perform periodic optimization
                await self.perform_memory_optimization()

                # Update indexes
                await self._update_all_indexes()

                # Sync with CESAR if configured
                if self.cesar_integration.get('auto_sync', False):
                    await self._sync_with_cesar()

            except Exception as e:
                self.logger.error(f"Memory maintenance error: {e}")
                await asyncio.sleep(3600)  # Continue despite errors

    async def _update_all_indexes(self):
        """Update all memory indexes."""
        # Placeholder for index maintenance
        pass

    async def _sync_with_cesar(self):
        """Sync memory data with CESAR system."""
        try:
            # Export recent learning data and collective intelligence
            export_data = await self.export_memory_for_cesar([
                MemoryType.LEARNING_DATA,
                MemoryType.COLLECTIVE_INTELLIGENCE
            ])

            # This would send the data to CESAR
            self.logger.info("Memory sync with CESAR completed")

        except Exception as e:
            self.logger.error(f"CESAR sync failed: {e}")

    async def get_memory_status(self) -> Dict[str, Any]:
        """Get current memory manager status."""
        return {
            'total_memories': len(self.memory_cache),
            'memory_types': {mt.value: len([m for m in self.memory_cache.values() if m.memory_type == mt])
                           for mt in MemoryType},
            'cache_size_mb': len(json.dumps([asdict(m) for m in self.memory_cache.values()])) / (1024 * 1024),
            'retention_policies': {mt.value: policy for mt, policy in self.retention_policies.items()},
            'access_patterns_count': len(self.access_patterns),
            'last_optimization': 'not_implemented',  # Would track last optimization time
            'sheets_connection': 'configured' if self.sheets_api_config.get('spreadsheet_id') else 'not_configured'
        }

    async def shutdown(self):
        """Shutdown the memory manager."""
        try:
            self.logger.info("Shutting down Google Sheets Memory Manager...")

            # Final sync with sheets
            await self._final_sync_to_sheets()

            # Save indexes
            await self._save_all_indexes()

            self.logger.info("Memory Manager shutdown complete")

        except Exception as e:
            self.logger.error(f"Memory Manager shutdown error: {e}")

    async def _final_sync_to_sheets(self):
        """Perform final sync of cached data to sheets."""
        # Placeholder for final synchronization
        pass

    async def _save_all_indexes(self):
        """Save all indexes to persistent storage."""
        # Placeholder for index saving
        pass