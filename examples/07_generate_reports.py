#!/usr/bin/env python3
"""
Example 7: Interactive Report Generation

This example demonstrates how to generate comprehensive, interactive
security reports with visualizations and metrics.
"""

import sys
import os
import argparse
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reporting.enhanced_report import EnhancedReportGenerator
from evaluation.metrics import SecurityMetrics
from config import get_config
from utils.logger import get_logger

# Initialize
logger = get_logger(__name__)
config = get_config()


def generate_sample_results():
    """Generate sample evaluation results for demonstration"""
    return {
        'authentication': {
            'total_attempts': 1000,
            'successful': 950,
            'failed': 50,
            'accuracy': 0.95
        },
        'attacks': {
            'photo': {'total': 100, 'successful': 12, 'detected': 88},
            'video': {'total': 100, 'successful': 25, 'detected': 75},
            'mask': {'total': 50, 'successful': 8, 'detected': 42},
            'adversarial': {'total': 75, 'successful': 45, 'detected': 30},
        },
        'metrics': {
            'FAR': 0.02,  # False Accept Rate
            'FRR': 0.05,  # False Reject Rate
            'EER': 0.035,  # Equal Error Rate
            'TAR': 0.95,  # True Accept Rate at FAR=0.1%
            'APCER': 0.15,  # Attack Presentation Classification Error Rate
            'BPCER': 0.05,  # Bona Fide Presentation Classification Error Rate
            'ACER': 0.10,  # Average Classification Error Rate
        },
        'performance': {
            'avg_auth_time_ms': 210,
            'avg_enrollment_time_ms': 1950,
            'cache_hit_rate': 0.85,
            'memory_usage_mb': 1402,
            'throughput_ops_per_sec': 4.8
        },
        'security': {
            'liveness_enabled': True,
            'rate_limiting_enabled': True,
            'template_encryption': True,
            'audit_logging': True,
            'input_validation': True
        }
    }


def main():
    """Generate interactive security reports"""
    parser = argparse.ArgumentParser(description="Report Generation Example")
    parser.add_argument('--results-file', type=str,
                       help='Path to evaluation results JSON file')
    parser.add_argument('--output-dir', type=str, default='data/results/reports',
                       help='Output directory for reports')
    parser.add_argument('--format', type=str, default='html',
                       choices=['html', 'json', 'text', 'all'],
                       help='Report format')
    parser.add_argument('--title', type=str, default='Biometric Security Assessment',
                       help='Report title')
    args = parser.parse_args()

    print("="*70)
    print("Example 7: Interactive Report Generation")
    print("="*70)

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Load or generate results
    if args.results_file and os.path.exists(args.results_file):
        print(f"\n📂 Loading results from: {args.results_file}")
        with open(args.results_file, 'r') as f:
            results = json.load(f)
    else:
        print("\n⚙️  Generating sample results for demonstration...")
        results = generate_sample_results()

    # Initialize report generator
    print("\n🔧 Initializing report generator...")
    report_gen = EnhancedReportGenerator()

    # Generate reports based on format
    print(f"\n📊 Generating {args.format.upper()} report(s)...")
    print("-" * 70)

    generated_files = []

    if args.format in ['html', 'all']:
        # Generate HTML report
        print("\n📍 Creating interactive HTML report...")

        html_file = os.path.join(args.output_dir, 'security_report.html')

        try:
            report_gen.generate_interactive_report(
                results=results,
                output_path=html_file,
                title=args.title
            )
            print(f"   ✓ Generated: {html_file}")
            generated_files.append(('HTML Report', html_file))
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

    if args.format in ['json', 'all']:
        # Generate JSON report
        print("\n📍 Creating JSON report...")

        json_file = os.path.join(args.output_dir, 'security_report.json')

        json_report = {
            'metadata': {
                'title': args.title,
                'generated_at': datetime.now().isoformat(),
                'version': '2.0.0',
                'generator': 'Biometric Security Research System'
            },
            'summary': {
                'authentication_accuracy': results.get('authentication', {}).get('accuracy', 0),
                'attack_detection_rate': _calculate_detection_rate(results),
                'security_score': _calculate_security_score(results),
            },
            'detailed_results': results,
            'recommendations': _generate_recommendations(results)
        }

        with open(json_file, 'w') as f:
            json.dump(json_report, f, indent=2)

        print(f"   ✓ Generated: {json_file}")
        generated_files.append(('JSON Report', json_file))

    if args.format in ['text', 'all']:
        # Generate text report
        print("\n📍 Creating text report...")

        text_file = os.path.join(args.output_dir, 'security_report.txt')

        with open(text_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write(f"{args.title}\n")
            f.write("="*70 + "\n\n")

            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Version: 2.0.0\n\n")

            # Authentication metrics
            f.write("AUTHENTICATION METRICS\n")
            f.write("-"*70 + "\n")
            if 'authentication' in results:
                auth = results['authentication']
                f.write(f"Total Attempts: {auth.get('total_attempts', 0)}\n")
                f.write(f"Successful: {auth.get('successful', 0)}\n")
                f.write(f"Failed: {auth.get('failed', 0)}\n")
                f.write(f"Accuracy: {auth.get('accuracy', 0):.2%}\n\n")

            # Security metrics
            f.write("SECURITY METRICS\n")
            f.write("-"*70 + "\n")
            if 'metrics' in results:
                metrics = results['metrics']
                f.write(f"FAR (False Accept Rate): {metrics.get('FAR', 0):.2%}\n")
                f.write(f"FRR (False Reject Rate): {metrics.get('FRR', 0):.2%}\n")
                f.write(f"EER (Equal Error Rate): {metrics.get('EER', 0):.2%}\n")
                f.write(f"TAR (True Accept Rate): {metrics.get('TAR', 0):.2%}\n\n")

            # Attack detection
            f.write("ATTACK DETECTION\n")
            f.write("-"*70 + "\n")
            if 'attacks' in results:
                for attack_type, attack_data in results['attacks'].items():
                    if isinstance(attack_data, dict):
                        total = attack_data.get('total', 0)
                        detected = attack_data.get('detected', 0)
                        rate = (detected / total * 100) if total > 0 else 0
                        f.write(f"{attack_type.capitalize()}: {detected}/{total} ({rate:.1f}% detected)\n")
                f.write("\n")

            # Performance
            f.write("PERFORMANCE\n")
            f.write("-"*70 + "\n")
            if 'performance' in results:
                perf = results['performance']
                f.write(f"Avg Auth Time: {perf.get('avg_auth_time_ms', 0)} ms\n")
                f.write(f"Throughput: {perf.get('throughput_ops_per_sec', 0):.1f} ops/sec\n")
                f.write(f"Memory Usage: {perf.get('memory_usage_mb', 0)} MB\n")
                f.write(f"Cache Hit Rate: {perf.get('cache_hit_rate', 0):.1%}\n\n")

            # Recommendations
            f.write("RECOMMENDATIONS\n")
            f.write("-"*70 + "\n")
            recommendations = _generate_recommendations(results)
            for i, rec in enumerate(recommendations, 1):
                f.write(f"{i}. {rec}\n")

        print(f"   ✓ Generated: {text_file}")
        generated_files.append(('Text Report', text_file))

    # Summary
    print("\n" + "="*70)
    print("Report Generation Summary")
    print("="*70)

    print(f"\n✓ Generated {len(generated_files)} report(s)")
    print(f"📁 Output directory: {args.output_dir}")

    print("\n📄 Generated Files:")
    for report_type, file_path in generated_files:
        print(f"   • {report_type}: {file_path}")

    # Display key metrics
    print("\n📊 Key Metrics:")
    if 'metrics' in results:
        metrics = results['metrics']
        print(f"   • FAR: {metrics.get('FAR', 0):.2%}")
        print(f"   • FRR: {metrics.get('FRR', 0):.2%}")
        print(f"   • EER: {metrics.get('EER', 0):.2%}")

    detection_rate = _calculate_detection_rate(results)
    print(f"   • Attack Detection Rate: {detection_rate:.1%}")

    security_score = _calculate_security_score(results)
    print(f"   • Overall Security Score: {security_score:.0f}/100")

    # Open HTML report in browser
    if args.format in ['html', 'all'] and generated_files:
        html_file = next((f for t, f in generated_files if t == 'HTML Report'), None)
        if html_file:
            print(f"\n💡 Tip: Open the HTML report in your browser:")
            print(f"   file://{os.path.abspath(html_file)}")

    print("\n" + "="*70)
    print("Next Steps:")
    print("1. Review generated reports")
    print("2. Share reports with stakeholders")
    print("3. Run: python examples/08_custom_configuration.py")
    print("4. Implement report recommendations")
    print("="*70)


def _calculate_detection_rate(results):
    """Calculate overall attack detection rate"""
    if 'attacks' not in results:
        return 0.0

    total_attacks = 0
    total_detected = 0

    for attack_data in results['attacks'].values():
        if isinstance(attack_data, dict):
            total_attacks += attack_data.get('total', 0)
            total_detected += attack_data.get('detected', 0)

    return (total_detected / total_attacks) if total_attacks > 0 else 0.0


def _calculate_security_score(results):
    """Calculate overall security score (0-100)"""
    score = 0
    weights = 0

    # Authentication accuracy (30%)
    if 'authentication' in results:
        auth_accuracy = results['authentication'].get('accuracy', 0)
        score += auth_accuracy * 30
        weights += 30

    # Attack detection rate (40%)
    detection_rate = _calculate_detection_rate(results)
    score += detection_rate * 40
    weights += 40

    # Security features enabled (30%)
    if 'security' in results:
        security = results['security']
        features_enabled = sum(1 for v in security.values() if v)
        features_total = len(security)
        if features_total > 0:
            score += (features_enabled / features_total) * 30
            weights += 30

    return (score / weights * 100) if weights > 0 else 0.0


def _generate_recommendations(results):
    """Generate security recommendations based on results"""
    recommendations = []

    # Check metrics
    if 'metrics' in results:
        metrics = results['metrics']

        if metrics.get('FAR', 0) > 0.05:
            recommendations.append(
                "Reduce False Accept Rate (FAR) by lowering authentication threshold"
            )

        if metrics.get('FRR', 0) > 0.10:
            recommendations.append(
                "Reduce False Reject Rate (FRR) by increasing threshold or improving enrollment"
            )

        if metrics.get('EER', 0) > 0.05:
            recommendations.append(
                "Improve Equal Error Rate (EER) by tuning threshold or using better model"
            )

    # Check attack detection
    detection_rate = _calculate_detection_rate(results)
    if detection_rate < 0.80:
        recommendations.append(
            "Improve attack detection rate by enabling multiple liveness detection methods"
        )

    # Check security features
    if 'security' in results:
        security = results['security']

        if not security.get('liveness_enabled'):
            recommendations.append("Enable liveness detection for all authentications")

        if not security.get('template_encryption'):
            recommendations.append("Enable template encryption to protect stored biometric data")

        if not security.get('rate_limiting_enabled'):
            recommendations.append("Enable rate limiting to prevent brute force attacks")

    # Check performance
    if 'performance' in results:
        perf = results['performance']

        if perf.get('avg_auth_time_ms', 0) > 500:
            recommendations.append("Optimize authentication time by enabling caching or using GPU")

        if perf.get('cache_hit_rate', 0) < 0.70:
            recommendations.append("Increase cache size to improve cache hit rate")

    # Generic recommendations
    if not recommendations:
        recommendations = [
            "Continue monitoring authentication metrics",
            "Perform regular security audits",
            "Keep all dependencies updated",
            "Test against new attack vectors periodically",
            "Review and update security policies"
        ]

    return recommendations


if __name__ == "__main__":
    main()
