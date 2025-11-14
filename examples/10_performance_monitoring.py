#!/usr/bin/env python3
"""
Example 10: Performance Monitoring

This example demonstrates how to monitor system performance,
including CPU usage, memory consumption, processing times, and throughput.
"""

import sys
import os
import time
import argparse
from typing import List, Dict
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.performance import (
    PerformanceMonitor, LRUCache, EmbeddingCache,
    optimize_memory, get_performance_monitor
)
from biometric.face_recognition import FaceAuthenticator
from config import get_config
from utils.logger import get_logger, log_execution_time
import numpy as np

# Initialize
logger = get_logger(__name__)
config = get_config()


def demo_system_monitoring():
    """Demonstrate real-time system monitoring"""
    print("\n" + "="*70)
    print("DEMO 1: System Resource Monitoring")
    print("="*70)

    monitor = PerformanceMonitor()

    print("\n📊 Current System Status:")
    print("-"*70)

    # CPU usage
    cpu_usage = monitor.get_cpu_usage()
    print(f"CPU Usage: {cpu_usage:.1f}%")

    # Memory usage
    memory_info = monitor.get_memory_usage()
    print(f"\nMemory Usage:")
    print(f"   Total: {memory_info['total']:.0f} MB")
    print(f"   Available: {memory_info['available']:.0f} MB")
    print(f"   Used: {memory_info['used']:.0f} MB")
    print(f"   Percentage: {memory_info['percent']:.1f}%")

    # Process memory
    process_memory = monitor.get_process_memory()
    print(f"\nProcess Memory:")
    print(f"   RSS: {process_memory['rss']:.0f} MB")
    print(f"   VMS: {process_memory['vms']:.0f} MB")

    # Continuous monitoring demo
    print("\n📈 Monitoring for 5 seconds (simulating load)...")
    print("-"*70)

    for i in range(5):
        # Simulate some work
        _ = np.random.rand(1000, 1000).sum()

        cpu = monitor.get_cpu_usage()
        mem = monitor.get_memory_usage()

        print(f"t={i+1}s: CPU={cpu:5.1f}% | Memory={mem['percent']:5.1f}% | "
              f"Process={monitor.get_process_memory()['rss']:6.0f}MB")

        time.sleep(1)


def demo_performance_profiling():
    """Demonstrate performance profiling"""
    print("\n" + "="*70)
    print("DEMO 2: Performance Profiling")
    print("="*70)

    monitor = PerformanceMonitor()

    # Function to profile
    @log_execution_time()
    def simulate_authentication(num_operations: int):
        """Simulate authentication operations"""
        for _ in range(num_operations):
            # Simulate face detection and extraction
            _ = np.random.rand(200, 200, 3)
            time.sleep(0.01)  # Simulate processing

    print("\n⏱️  Profiling Operations:")
    print("-"*70)

    # Profile different workloads
    workloads = [10, 50, 100]

    for num_ops in workloads:
        print(f"\nProfiling {num_ops} operations...")

        start_time = time.time()
        start_memory = monitor.get_process_memory()['rss']

        simulate_authentication(num_ops)

        end_time = time.time()
        end_memory = monitor.get_process_memory()['rss']

        elapsed = (end_time - start_time) * 1000  # Convert to ms
        memory_delta = end_memory - start_memory

        print(f"   Total time: {elapsed:.0f} ms")
        print(f"   Avg time per op: {elapsed/num_ops:.2f} ms")
        print(f"   Throughput: {num_ops/(elapsed/1000):.1f} ops/sec")
        print(f"   Memory delta: {memory_delta:+.1f} MB")


def demo_cache_performance():
    """Demonstrate cache performance"""
    print("\n" + "="*70)
    print("DEMO 3: Cache Performance")
    print("="*70)

    # Test LRU cache
    print("\n💾 Testing LRU Cache:")
    print("-"*70)

    cache = LRUCache(max_size=100)

    # Populate cache
    print("Populating cache with 150 entries (max size: 100)...")
    for i in range(150):
        cache.set(f"key_{i}", f"value_{i}")

    print(f"Cache size: {len(cache.cache)}")
    print(f"Oldest entries evicted: {150 - len(cache.cache)}")

    # Test cache hits
    print("\nTesting cache hits and misses:")

    hit_count = 0
    miss_count = 0

    test_keys = [f"key_{i}" for i in range(0, 150, 10)]

    for key in test_keys:
        value = cache.get(key)
        if value is not None:
            hit_count += 1
            print(f"   {key}: HIT")
        else:
            miss_count += 1
            print(f"   {key}: MISS (evicted)")

    hit_rate = hit_count / len(test_keys)
    print(f"\nCache Hit Rate: {hit_rate:.1%}")

    # Test embedding cache
    print("\n💾 Testing Embedding Cache:")
    print("-"*70)

    embedding_cache = EmbeddingCache(max_size=50)

    # Simulate embedding storage
    print("Storing 50 face embeddings...")
    for i in range(50):
        embedding = np.random.rand(128)  # Simulated 128-d embedding
        embedding_cache.set(f"user_{i}", embedding)

    print(f"Cache size: {len(embedding_cache.cache.cache)}")

    # Benchmark cache vs no cache
    print("\nBenchmarking cached vs uncached retrieval:")

    # Cached retrieval
    start = time.time()
    for i in range(1000):
        _ = embedding_cache.get(f"user_{i % 50}")
    cached_time = (time.time() - start) * 1000

    # Uncached (simulated)
    start = time.time()
    for i in range(1000):
        _ = np.random.rand(128)  # Simulated generation
    uncached_time = (time.time() - start) * 1000

    print(f"   Cached: {cached_time:.2f} ms (1000 retrievals)")
    print(f"   Uncached: {uncached_time:.2f} ms (1000 generations)")
    print(f"   Speedup: {uncached_time/cached_time:.1f}x")


def demo_memory_optimization():
    """Demonstrate memory optimization"""
    print("\n" + "="*70)
    print("DEMO 4: Memory Optimization")
    print("="*70)

    monitor = PerformanceMonitor()

    print("\n🧹 Memory Before Optimization:")
    print("-"*70)

    before_memory = monitor.get_process_memory()
    print(f"   RSS: {before_memory['rss']:.0f} MB")
    print(f"   VMS: {before_memory['vms']:.0f} MB")

    # Create some data to clean up
    print("\n   Allocating temporary data...")
    large_data = [np.random.rand(1000, 1000) for _ in range(5)]
    del large_data

    print("\n🧹 Running Memory Optimization...")
    print("-"*70)

    optimize_memory()

    print("\n🧹 Memory After Optimization:")
    print("-"*70)

    after_memory = monitor.get_process_memory()
    print(f"   RSS: {after_memory['rss']:.0f} MB")
    print(f"   VMS: {after_memory['vms']:.0f} MB")

    memory_freed = before_memory['rss'] - after_memory['rss']
    print(f"\n   Memory freed: {memory_freed:.0f} MB")


def demo_throughput_testing():
    """Demonstrate throughput testing"""
    print("\n" + "="*70)
    print("DEMO 5: Throughput Testing")
    print("="*70)

    print("\n📈 Testing System Throughput:")
    print("-"*70)

    # Simulate various workloads
    def simulate_workload(name: str, operation_time_ms: float, num_operations: int):
        print(f"\n{name}:")
        start = time.time()

        for _ in range(num_operations):
            time.sleep(operation_time_ms / 1000)  # Simulate operation

        elapsed = time.time() - start
        throughput = num_operations / elapsed

        print(f"   Operations: {num_operations}")
        print(f"   Total time: {elapsed:.2f} s")
        print(f"   Throughput: {throughput:.2f} ops/sec")
        print(f"   Avg latency: {elapsed/num_operations*1000:.2f} ms/op")

        return throughput

    # Test different scenarios
    results = {}

    # Fast operations (cached)
    results['cached'] = simulate_workload(
        "Cached Authentication",
        operation_time_ms=15,
        num_operations=100
    )

    # Normal operations
    results['normal'] = simulate_workload(
        "Normal Authentication",
        operation_time_ms=210,
        num_operations=20
    )

    # Enrollment (slower)
    results['enrollment'] = simulate_workload(
        "User Enrollment",
        operation_time_ms=1950,
        num_operations=5
    )

    # Summary
    print("\n📊 Throughput Summary:")
    print("-"*70)
    for scenario, throughput in results.items():
        print(f"   {scenario.capitalize():20s}: {throughput:6.2f} ops/sec")


def demo_real_time_monitoring():
    """Demonstrate real-time monitoring dashboard"""
    print("\n" + "="*70)
    print("DEMO 6: Real-Time Monitoring Dashboard")
    print("="*70)

    monitor = PerformanceMonitor()

    print("\n📊 Real-Time Dashboard (10 seconds):")
    print("-"*70)
    print("\nTime | CPU%  | Mem%  | Process MB | Status")
    print("-" * 70)

    # Monitor for 10 seconds
    for i in range(10):
        cpu = monitor.get_cpu_usage()
        mem = monitor.get_memory_usage()
        proc = monitor.get_process_memory()

        # Determine status
        if cpu > 80 or mem['percent'] > 80:
            status = "⚠️  HIGH"
        elif cpu > 60 or mem['percent'] > 60:
            status = "⚡ MODERATE"
        else:
            status = "✓ NORMAL"

        print(f"{i+1:3d}s | {cpu:5.1f} | {mem['percent']:5.1f} | {proc['rss']:10.0f} | {status}")

        # Simulate varying load
        if i % 3 == 0:
            _ = np.random.rand(500, 500).sum()

        time.sleep(1)


def generate_performance_report(output_file: str):
    """Generate comprehensive performance report"""
    print("\n" + "="*70)
    print("Generating Performance Report")
    print("="*70)

    monitor = PerformanceMonitor()

    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'system': {
            'cpu_usage': monitor.get_cpu_usage(),
            'memory': monitor.get_memory_usage(),
            'process': monitor.get_process_memory(),
        },
        'configuration': {
            'model': config.biometric.model_name,
            'cache_enabled': config.performance.cache_embeddings,
            'cache_size': config.performance.cache_size,
            'gpu_enabled': config.performance.enable_gpu,
            'num_workers': config.performance.num_workers,
        },
        'recommendations': [],
    }

    # Generate recommendations
    if report['system']['cpu_usage'] > 80:
        report['recommendations'].append(
            "High CPU usage detected. Consider enabling GPU acceleration or reducing workload."
        )

    if report['system']['memory']['percent'] > 80:
        report['recommendations'].append(
            "High memory usage. Consider reducing cache size or optimizing memory usage."
        )

    if not config.performance.cache_embeddings:
        report['recommendations'].append(
            "Embedding cache is disabled. Enable for better performance."
        )

    if not report['recommendations']:
        report['recommendations'].append("System performing within normal parameters.")

    # Save report
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n✓ Performance report saved: {output_file}")

    # Display summary
    print("\n📊 Report Summary:")
    print("-"*70)
    print(f"CPU Usage: {report['system']['cpu_usage']:.1f}%")
    print(f"Memory Usage: {report['system']['memory']['percent']:.1f}%")
    print(f"Process Memory: {report['system']['process']['rss']:.0f} MB")

    print("\n💡 Recommendations:")
    for rec in report['recommendations']:
        print(f"   • {rec}")


def main():
    """Main performance monitoring demo"""
    parser = argparse.ArgumentParser(description="Performance Monitoring Example")
    parser.add_argument('--demo', type=str, default='all',
                       choices=['system', 'profiling', 'cache', 'memory',
                               'throughput', 'dashboard', 'all'],
                       help='Which demo to run')
    parser.add_argument('--report', type=str,
                       help='Generate performance report to file')
    args = parser.parse_args()

    print("="*70)
    print("Example 10: Performance Monitoring")
    print("="*70)

    # Run selected demos
    if args.demo in ['system', 'all']:
        demo_system_monitoring()

    if args.demo in ['profiling', 'all']:
        demo_performance_profiling()

    if args.demo in ['cache', 'all']:
        demo_cache_performance()

    if args.demo in ['memory', 'all']:
        demo_memory_optimization()

    if args.demo in ['throughput', 'all']:
        demo_throughput_testing()

    if args.demo in ['dashboard', 'all']:
        demo_real_time_monitoring()

    # Generate report if requested
    if args.report:
        generate_performance_report(args.report)

    # Summary
    print("\n" + "="*70)
    print("Performance Monitoring Summary")
    print("="*70)

    print("\n✓ Demonstrated Monitoring Features:")
    print("   • Real-time CPU and memory monitoring")
    print("   • Performance profiling and benchmarking")
    print("   • Cache performance analysis")
    print("   • Memory optimization techniques")
    print("   • Throughput testing")
    print("   • Real-time dashboard")

    print("\n📚 Related Documentation:")
    print("   • docs/BENCHMARKS.md - Performance benchmarks")
    print("   • docs/FAQ.md - Performance FAQ")
    print("   • docs/DEPLOYMENT.md - Production optimization")

    print("\n💡 Optimization Tips:")
    print("   1. Enable embedding cache for 14x speedup")
    print("   2. Use GPU acceleration for 2.8x faster inference")
    print("   3. Batch processing for 2.5x better throughput")
    print("   4. Monitor and optimize memory usage regularly")
    print("   5. Tune cache size based on workload")

    print("\n" + "="*70)
    print("Examples Complete!")
    print("="*70)

    print("\nYou have completed all 10 examples:")
    print("   ✓ 01: Simple Enrollment")
    print("   ✓ 02: Authentication")
    print("   ✓ 03: Generate Attacks")
    print("   ✓ 04: Advanced Attacks")
    print("   ✓ 05: Liveness Detection")
    print("   ✓ 06: Vulnerability Testing")
    print("   ✓ 07: Generate Reports")
    print("   ✓ 08: Custom Configuration")
    print("   ✓ 09: Security Features")
    print("   ✓ 10: Performance Monitoring")

    print("\n🎓 Next Steps:")
    print("   1. Experiment with your own data")
    print("   2. Customize configurations for your use case")
    print("   3. Run comprehensive security tests")
    print("   4. Deploy to production environment")
    print("   5. Contribute improvements back to the project!")

    print("="*70)


if __name__ == "__main__":
    main()
