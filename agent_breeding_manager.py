#!/usr/bin/env python3
"""
Agent Breeding Manager for Recursive Cognition Ecosystem
Handles the creation, evolution, and management of specialized agents based on performance patterns.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
import json
import hashlib
from dataclasses import dataclass


@dataclass
class AgentGenome:
    """Represents the genetic makeup of an agent."""
    agent_type: str
    capabilities: List[str]
    config_dna: Dict[str, Any]
    behavioral_traits: Dict[str, float]
    performance_genes: Dict[str, Any]
    parent_lineage: List[str]
    generation: int
    fitness_score: float = 0.0


@dataclass
class BreedingPattern:
    """Represents a pattern that triggers agent breeding."""
    pattern_id: str
    task_type: str
    frequency: int
    complexity: float
    success_rate: float
    avg_duration_ms: int
    agents_involved: List[str]
    first_observed: datetime
    last_observed: datetime


class AgentBreedingManager:
    """
    Manages the breeding and evolution of agents in the recursive cognition ecosystem.
    """

    def __init__(self):
        self.logger = logging.getLogger("agent_breeding_manager")
        self.breeding_patterns = {}
        self.agent_genomes = {}
        self.evolution_history = []
        self.breeding_rules = {
            'min_pattern_frequency': 15,
            'min_complexity_threshold': 0.75,
            'max_generations': 10,
            'fitness_threshold': 0.8,
            'crossover_rate': 0.7,
            'mutation_rate': 0.1
        }

    async def initialize(self):
        """Initialize the breeding manager."""
        try:
            self.logger.info("Initializing Agent Breeding Manager...")

            # Load existing breeding patterns and genomes
            await self._load_breeding_data()

            # Initialize breeding environment
            await self._setup_breeding_environment()

            self.logger.info("Agent Breeding Manager initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"Breeding manager initialization failed: {e}")
            return False

    async def observe_task_pattern(self, task_data: Dict[str, Any], agents_involved: List[str],
                                   performance_metrics: Dict[str, Any]):
        """Observe and record task patterns for potential breeding opportunities."""
        try:
            # Generate pattern ID based on task characteristics
            pattern_characteristics = {
                'task_type': task_data.get('task_type'),
                'complexity_indicators': task_data.get('complexity_indicators', []),
                'required_capabilities': task_data.get('required_capabilities', [])
            }

            pattern_id = self._generate_pattern_id(pattern_characteristics)

            # Update or create breeding pattern
            if pattern_id in self.breeding_patterns:
                pattern = self.breeding_patterns[pattern_id]
                pattern.frequency += 1
                pattern.last_observed = datetime.now()

                # Update running averages
                pattern.success_rate = (pattern.success_rate + performance_metrics.get('success_rate', 0)) / 2
                pattern.avg_duration_ms = (pattern.avg_duration_ms + performance_metrics.get('duration_ms', 0)) / 2

            else:
                # Create new pattern
                pattern = BreedingPattern(
                    pattern_id=pattern_id,
                    task_type=task_data.get('task_type', 'unknown'),
                    frequency=1,
                    complexity=self._calculate_task_complexity(task_data),
                    success_rate=performance_metrics.get('success_rate', 0),
                    avg_duration_ms=performance_metrics.get('duration_ms', 0),
                    agents_involved=agents_involved,
                    first_observed=datetime.now(),
                    last_observed=datetime.now()
                )

                self.breeding_patterns[pattern_id] = pattern

            # Check if pattern qualifies for breeding
            await self._evaluate_breeding_opportunity(pattern)

        except Exception as e:
            self.logger.error(f"Task pattern observation failed: {e}")

    async def breed_specialized_agent(self, pattern: BreedingPattern,
                                     parent_agents: List[Any]) -> Optional[Dict[str, Any]]:
        """Breed a new specialized agent based on successful patterns."""
        try:
            self.logger.info(f"Breeding specialized agent for pattern: {pattern.pattern_id}")

            # Select best parent agents
            selected_parents = await self._select_breeding_parents(parent_agents, pattern)

            if len(selected_parents) < 1:
                self.logger.warning("Insufficient suitable parents for breeding")
                return None

            # Create genetic crossover
            new_genome = await self._create_crossover_genome(selected_parents, pattern)

            # Apply mutations for diversity
            new_genome = await self._apply_mutations(new_genome)

            # Generate specialized agent configuration
            specialized_config = await self._genome_to_config(new_genome)

            # Create breeding record
            breeding_record = {
                'timestamp': datetime.now().isoformat(),
                'pattern_id': pattern.pattern_id,
                'parent_agents': [agent.agent_id for agent in selected_parents],
                'new_genome': new_genome.__dict__,
                'specialized_config': specialized_config,
                'generation': new_genome.generation,
                'predicted_fitness': new_genome.fitness_score
            }

            self.evolution_history.append(breeding_record)

            # Store genome for future breeding
            self.agent_genomes[new_genome.agent_type] = new_genome

            self.logger.info(f"Successfully bred agent: {new_genome.agent_type}")
            return {
                'agent_type': new_genome.agent_type,
                'config': specialized_config,
                'genome': new_genome,
                'breeding_record': breeding_record
            }

        except Exception as e:
            self.logger.error(f"Agent breeding failed: {e}")
            return None

    async def evolve_existing_agent(self, agent: Any, performance_data: Dict[str, Any]) -> bool:
        """Evolve an existing agent based on performance feedback."""
        try:
            agent_id = agent.agent_id

            # Get or create genome for agent
            if agent_id not in self.agent_genomes:
                # Create genome from current agent
                genome = await self._agent_to_genome(agent)
                self.agent_genomes[agent_id] = genome
            else:
                genome = self.agent_genomes[agent_id]

            # Calculate fitness based on performance
            current_fitness = self._calculate_fitness(performance_data)

            # Only evolve if performance is declining
            if current_fitness < genome.fitness_score - 0.1:
                # Apply adaptive mutations
                evolved_genome = await self._apply_adaptive_evolution(genome, performance_data)

                # Update agent configuration
                new_config = await self._genome_to_config(evolved_genome)

                # Apply evolution to agent
                await agent.evolve_capabilities({
                    'optimization': {
                        'type': 'genetic_evolution',
                        'config_changes': new_config,
                        'genome_changes': evolved_genome.__dict__
                    }
                })

                # Update stored genome
                self.agent_genomes[agent_id] = evolved_genome

                self.logger.info(f"Evolved agent {agent_id} from fitness {genome.fitness_score:.3f} to {evolved_genome.fitness_score:.3f}")
                return True

        except Exception as e:
            self.logger.error(f"Agent evolution failed: {e}")

        return False

    async def manage_agent_population(self, current_agents: List[Any]) -> Dict[str, Any]:
        """Manage the overall agent population for optimal diversity and performance."""
        try:
            population_analysis = {
                'total_agents': len(current_agents),
                'genetic_diversity': self._calculate_genetic_diversity(current_agents),
                'average_fitness': self._calculate_average_fitness(current_agents),
                'recommendations': []
            }

            # Check for overpopulation
            if len(current_agents) > 20:
                # Recommend culling of low-fitness agents
                low_fitness_agents = [
                    agent for agent in current_agents
                    if self._get_agent_fitness(agent) < 0.5
                ]
                population_analysis['recommendations'].append({
                    'type': 'cull_agents',
                    'agents': [agent.agent_id for agent in low_fitness_agents[:5]],
                    'reason': 'Low fitness and overpopulation'
                })

            # Check for low diversity
            if population_analysis['genetic_diversity'] < 0.4:
                population_analysis['recommendations'].append({
                    'type': 'increase_diversity',
                    'action': 'Breed agents with different genetic makeup',
                    'target_diversity': 0.6
                })

            # Check for underperforming specializations
            specialization_performance = self._analyze_specialization_performance(current_agents)
            for spec, performance in specialization_performance.items():
                if performance < 0.6:
                    population_analysis['recommendations'].append({
                        'type': 'improve_specialization',
                        'specialization': spec,
                        'current_performance': performance,
                        'action': 'Breed or evolve agents for this specialization'
                    })

            return population_analysis

        except Exception as e:
            self.logger.error(f"Population management failed: {e}")
            return {'error': str(e)}

    # Helper methods
    def _generate_pattern_id(self, characteristics: Dict[str, Any]) -> str:
        """Generate a unique ID for a task pattern."""
        content = json.dumps(characteristics, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def _calculate_task_complexity(self, task_data: Dict[str, Any]) -> float:
        """Calculate complexity score for a task."""
        complexity = 0.0

        # Number of capabilities required
        capabilities = task_data.get('required_capabilities', [])
        complexity += len(capabilities) * 0.1

        # Data complexity indicators
        complexity_indicators = task_data.get('complexity_indicators', [])
        complexity += len(complexity_indicators) * 0.15

        # Task dependencies
        dependencies = task_data.get('dependencies', [])
        complexity += len(dependencies) * 0.05

        # Estimated processing time
        estimated_time = task_data.get('estimated_duration_ms', 0)
        if estimated_time > 60000:  # More than 1 minute
            complexity += 0.3

        return min(1.0, complexity)

    async def _evaluate_breeding_opportunity(self, pattern: BreedingPattern):
        """Evaluate if a pattern qualifies for breeding a new agent."""
        if (pattern.frequency >= self.breeding_rules['min_pattern_frequency'] and
            pattern.complexity >= self.breeding_rules['min_complexity_threshold']):

            self.logger.info(f"Pattern {pattern.pattern_id} qualifies for breeding")
            # This would trigger the actual breeding process
            # Implementation depends on access to the agent manager

    async def _select_breeding_parents(self, available_agents: List[Any],
                                     pattern: BreedingPattern) -> List[Any]:
        """Select the best parent agents for breeding."""
        # Score agents based on relevance to pattern and performance
        scored_agents = []

        for agent in available_agents:
            relevance_score = self._calculate_pattern_relevance(agent, pattern)
            performance_score = self._get_agent_fitness(agent)
            combined_score = (relevance_score * 0.6) + (performance_score * 0.4)

            scored_agents.append((agent, combined_score))

        # Sort by score and select top performers
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        return [agent for agent, score in scored_agents[:3]]  # Top 3 parents

    def _calculate_pattern_relevance(self, agent: Any, pattern: BreedingPattern) -> float:
        """Calculate how relevant an agent is to a breeding pattern."""
        agent_capabilities = set(agent.get_capabilities())
        pattern_requirements = set(pattern.task_type.split('_'))

        if len(pattern_requirements) == 0:
            return 0.0

        overlap = len(agent_capabilities.intersection(pattern_requirements))
        return overlap / len(pattern_requirements)

    def _get_agent_fitness(self, agent: Any) -> float:
        """Get fitness score for an agent."""
        if hasattr(agent, 'performance_metrics'):
            return agent.performance_metrics.get('success_rate', 0.0)
        return 0.5  # Default fitness

    async def _create_crossover_genome(self, parents: List[Any], pattern: BreedingPattern) -> AgentGenome:
        """Create a new genome through genetic crossover."""
        # Get parent genomes
        parent_genomes = []
        for parent in parents:
            if parent.agent_id in self.agent_genomes:
                parent_genomes.append(self.agent_genomes[parent.agent_id])
            else:
                # Create genome from agent
                genome = await self._agent_to_genome(parent)
                parent_genomes.append(genome)

        # Create new genome through crossover
        new_generation = max(g.generation for g in parent_genomes) + 1

        # Combine capabilities from all parents
        combined_capabilities = set()
        for genome in parent_genomes:
            combined_capabilities.update(genome.capabilities)

        # Crossover configuration DNA
        crossover_config = {}
        for genome in parent_genomes:
            for key, value in genome.config_dna.items():
                if key not in crossover_config:
                    crossover_config[key] = value

        # Blend behavioral traits
        blended_traits = {}
        for genome in parent_genomes:
            for trait, value in genome.behavioral_traits.items():
                if trait in blended_traits:
                    blended_traits[trait] = (blended_traits[trait] + value) / 2
                else:
                    blended_traits[trait] = value

        # Create specialized agent type name
        specialization = pattern.task_type.replace('_', '').title()
        new_agent_type = f"Specialized{specialization}Agent_Gen{new_generation}"

        new_genome = AgentGenome(
            agent_type=new_agent_type,
            capabilities=list(combined_capabilities),
            config_dna=crossover_config,
            behavioral_traits=blended_traits,
            performance_genes={'specialized_for': pattern.task_type},
            parent_lineage=[g.agent_type for g in parent_genomes],
            generation=new_generation,
            fitness_score=sum(g.fitness_score for g in parent_genomes) / len(parent_genomes)
        )

        return new_genome

    async def _apply_mutations(self, genome: AgentGenome) -> AgentGenome:
        """Apply random mutations to introduce genetic diversity."""
        import random

        if random.random() < self.breeding_rules['mutation_rate']:
            # Capability mutation
            if random.random() < 0.3:
                new_capability = random.choice([
                    'advanced_analysis', 'predictive_modeling', 'optimization',
                    'pattern_recognition', 'automated_learning', 'real_time_processing'
                ])
                if new_capability not in genome.capabilities:
                    genome.capabilities.append(new_capability)

            # Behavioral trait mutation
            if random.random() < 0.4:
                trait_to_mutate = random.choice(list(genome.behavioral_traits.keys()) or ['aggressiveness'])
                mutation_amount = random.uniform(-0.1, 0.1)
                if trait_to_mutate in genome.behavioral_traits:
                    genome.behavioral_traits[trait_to_mutate] = max(0, min(1,
                        genome.behavioral_traits[trait_to_mutate] + mutation_amount))
                else:
                    genome.behavioral_traits[trait_to_mutate] = random.uniform(0, 1)

            # Configuration mutation
            if random.random() < 0.2:
                mutation_configs = {
                    'learning_rate': random.uniform(0.001, 0.1),
                    'exploration_factor': random.uniform(0.1, 0.5),
                    'memory_retention': random.uniform(0.7, 1.0)
                }

                for key, value in mutation_configs.items():
                    if random.random() < 0.5:
                        genome.config_dna[key] = value

        return genome

    async def _apply_adaptive_evolution(self, genome: AgentGenome,
                                      performance_data: Dict[str, Any]) -> AgentGenome:
        """Apply evolution based on performance feedback."""
        evolved_genome = AgentGenome(**genome.__dict__)
        evolved_genome.generation += 1

        # Identify performance issues
        success_rate = performance_data.get('success_rate', 0)
        avg_duration = performance_data.get('avg_duration_ms', 0)

        # Adapt based on performance
        if success_rate < 0.7:
            # Add capabilities to improve success rate
            evolved_genome.capabilities.extend(['enhanced_processing', 'error_recovery'])

        if avg_duration > 30000:
            # Optimize for speed
            evolved_genome.config_dna['optimization_level'] = 'high'
            evolved_genome.behavioral_traits['processing_speed'] = 0.9

        # Update fitness score
        evolved_genome.fitness_score = self._calculate_fitness(performance_data)

        return evolved_genome

    async def _genome_to_config(self, genome: AgentGenome) -> Dict[str, Any]:
        """Convert a genome to agent configuration."""
        config = {
            'agent_type': genome.agent_type,
            'capabilities': genome.capabilities,
            'generation': genome.generation,
            'parent_lineage': genome.parent_lineage,
            'genetic_fitness': genome.fitness_score,
            **genome.config_dna
        }

        # Add behavioral configurations
        for trait, value in genome.behavioral_traits.items():
            config[f"behavior_{trait}"] = value

        return config

    async def _agent_to_genome(self, agent: Any) -> AgentGenome:
        """Create a genome representation from an existing agent."""
        return AgentGenome(
            agent_type=agent.agent_type,
            capabilities=agent.get_capabilities(),
            config_dna=agent.config.copy(),
            behavioral_traits={'base_performance': self._get_agent_fitness(agent)},
            performance_genes={'success_rate': self._get_agent_fitness(agent)},
            parent_lineage=[],
            generation=1,
            fitness_score=self._get_agent_fitness(agent)
        )

    def _calculate_fitness(self, performance_data: Dict[str, Any]) -> float:
        """Calculate fitness score from performance data."""
        success_rate = performance_data.get('success_rate', 0)
        efficiency = 1.0 - min(1.0, performance_data.get('avg_duration_ms', 30000) / 60000)
        reliability = performance_data.get('reliability_score', 0.5)

        return (success_rate * 0.5) + (efficiency * 0.3) + (reliability * 0.2)

    def _calculate_genetic_diversity(self, agents: List[Any]) -> float:
        """Calculate genetic diversity of the agent population."""
        if len(agents) < 2:
            return 0.0

        # Simple diversity measure based on capability overlap
        all_capabilities = set()
        agent_capabilities = []

        for agent in agents:
            caps = set(agent.get_capabilities())
            all_capabilities.update(caps)
            agent_capabilities.append(caps)

        if not all_capabilities:
            return 0.0

        # Calculate average pairwise similarity
        total_similarity = 0
        comparisons = 0

        for i in range(len(agent_capabilities)):
            for j in range(i + 1, len(agent_capabilities)):
                caps1, caps2 = agent_capabilities[i], agent_capabilities[j]
                overlap = len(caps1.intersection(caps2))
                union = len(caps1.union(caps2))
                similarity = overlap / union if union > 0 else 0
                total_similarity += similarity
                comparisons += 1

        avg_similarity = total_similarity / comparisons if comparisons > 0 else 0
        diversity = 1.0 - avg_similarity

        return diversity

    def _calculate_average_fitness(self, agents: List[Any]) -> float:
        """Calculate average fitness of the agent population."""
        if not agents:
            return 0.0

        total_fitness = sum(self._get_agent_fitness(agent) for agent in agents)
        return total_fitness / len(agents)

    def _analyze_specialization_performance(self, agents: List[Any]) -> Dict[str, float]:
        """Analyze performance by agent specialization."""
        specializations = {}

        for agent in agents:
            spec = getattr(agent, 'specialization', agent.agent_type)
            fitness = self._get_agent_fitness(agent)

            if spec in specializations:
                specializations[spec] = (specializations[spec] + fitness) / 2
            else:
                specializations[spec] = fitness

        return specializations

    async def _load_breeding_data(self):
        """Load existing breeding patterns and genomes."""
        # Placeholder for loading from persistent storage
        pass

    async def _setup_breeding_environment(self):
        """Setup the breeding environment."""
        # Placeholder for environment setup
        pass

    async def get_breeding_status(self) -> Dict[str, Any]:
        """Get current breeding manager status."""
        return {
            'active_patterns': len(self.breeding_patterns),
            'stored_genomes': len(self.agent_genomes),
            'evolution_events': len(self.evolution_history),
            'breeding_rules': self.breeding_rules,
            'recent_breeding': self.evolution_history[-5:] if self.evolution_history else []
        }

    async def shutdown(self):
        """Shutdown the breeding manager."""
        try:
            # Save breeding data
            await self._save_breeding_data()
            self.logger.info("Agent Breeding Manager shutdown complete")
        except Exception as e:
            self.logger.error(f"Breeding manager shutdown error: {e}")

    async def _save_breeding_data(self):
        """Save breeding patterns and genomes to persistent storage."""
        # Placeholder for saving to persistent storage
        pass