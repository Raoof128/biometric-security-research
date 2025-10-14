"""
Security report generation with visualizations and comprehensive analysis.
"""

import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import numpy as np


class SecurityReportGenerator:
    """
    Generate comprehensive security assessment reports with charts and analysis.
    """

    def __init__(self, results_file=None):
        """
        Initialize report generator

        Args:
            results_file: Path to vulnerability test results JSON
        """
        self.results_file = results_file
        self.results = None
        self.metrics = None

        if results_file and os.path.exists(results_file):
            self.load_results(results_file)

        print("[+] SecurityReportGenerator initialized")

    def load_results(self, results_file):
        """Load vulnerability test results"""
        with open(results_file, 'r') as f:
            self.results = json.load(f)

        self.metrics = self.results.get('metrics', {})
        print(f"[+] Loaded results from {results_file}")

    def generate_charts(self, output_dir='data/results/charts'):
        """
        Generate visualization charts

        Args:
            output_dir: Directory to save charts
        """
        os.makedirs(output_dir, exist_ok=True)
        print("[*] Generating charts...")

        if not self.metrics:
            print("[-] No metrics available for chart generation")
            return

        # Chart 1: Attack Success Rates
        self._generate_attack_success_chart(output_dir)

        # Chart 2: Error Rates (FAR, FRR, EER)
        self._generate_error_rates_chart(output_dir)

        # Chart 3: System Performance Overview
        self._generate_performance_overview(output_dir)

        # Chart 4: Anti-Spoofing Effectiveness
        self._generate_antispoofing_chart(output_dir)

        print(f"[+] Charts generated in {output_dir}")

    def _generate_attack_success_chart(self, output_dir):
        """Generate attack success rates bar chart"""
        if not self.results:
            return

        attack_types = []
        success_rates = []

        # Photo attacks
        if self.results.get('photo_attacks'):
            photo_success = sum(1 for r in self.results['photo_attacks']
                               if r['fooled_system']) / len(self.results['photo_attacks'])
            attack_types.append('Photo')
            success_rates.append(photo_success)

        # Mask attacks
        if self.results.get('mask_attacks'):
            mask_success = sum(1 for r in self.results['mask_attacks']
                              if r['fooled_system']) / len(self.results['mask_attacks'])
            attack_types.append('Mask')
            success_rates.append(mask_success)

        # Degraded attacks
        if self.results.get('degraded_attacks'):
            degraded_success = sum(1 for r in self.results['degraded_attacks']
                                  if r['fooled_system']) / len(self.results['degraded_attacks'])
            attack_types.append('Degraded')
            success_rates.append(degraded_success)

        # Synthetic fingerprints
        if self.results.get('synthetic_fingerprints'):
            synth_success = sum(1 for r in self.results['synthetic_fingerprints']
                               if r['fooled_system']) / len(self.results['synthetic_fingerprints'])
            attack_types.append('Synthetic FP')
            success_rates.append(synth_success)

        if not attack_types:
            return

        plt.figure(figsize=(10, 6))
        colors = ['#e74c3c', '#e67e22', '#f39c12', '#3498db'][:len(attack_types)]
        bars = plt.bar(attack_types, success_rates, color=colors, alpha=0.8)

        plt.ylabel('Success Rate', fontsize=12, fontweight='bold')
        plt.title('Presentation Attack Success Rates', fontsize=14, fontweight='bold')
        plt.ylim(0, 1.0)
        plt.grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for bar, rate in zip(bars, success_rates):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{rate:.1%}', ha='center', va='bottom',
                    fontweight='bold', fontsize=11)

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'attack_success_rates.png'),
                   dpi=300, bbox_inches='tight')
        plt.close()

    def _generate_error_rates_chart(self, output_dir):
        """Generate error rates comparison chart"""
        if not self.metrics:
            return

        metrics_data = ['FAR', 'FRR', 'EER']
        values = [
            self.metrics.get('FAR', 0),
            self.metrics.get('FRR', 0),
            self.metrics.get('EER', 0)
        ]
        colors = ['#e74c3c', '#3498db', '#f39c12']

        plt.figure(figsize=(8, 6))
        bars = plt.bar(metrics_data, values, color=colors, alpha=0.8)

        plt.ylabel('Rate', fontsize=12, fontweight='bold')
        plt.title('Biometric System Error Rates', fontsize=14, fontweight='bold')
        plt.ylim(0, max(values) * 1.3 if max(values) > 0 else 1.0)
        plt.grid(axis='y', alpha=0.3)

        # Add value labels
        for bar, value in zip(bars, values):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{value:.2%}', ha='center', va='bottom',
                    fontweight='bold', fontsize=11)

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'error_rates.png'),
                   dpi=300, bbox_inches='tight')
        plt.close()

    def _generate_performance_overview(self, output_dir):
        """Generate overall system performance pie chart"""
        if not self.metrics:
            return

        labels = ['Genuine Accuracy', 'Attack Success', 'Anti-Spoof Detection']
        values = [
            self.metrics.get('Genuine_Accuracy', 0) * 100,
            self.metrics.get('Attack_Success_Rate', 0) * 100,
            self.metrics.get('AntiSpoof_Detection_Rate', 0) * 100
        ]
        colors = ['#2ecc71', '#e74c3c', '#3498db']
        explode = (0.05, 0.05, 0.05)

        plt.figure(figsize=(10, 7))
        wedges, texts, autotexts = plt.pie(values, labels=labels, colors=colors,
                                           autopct='%1.1f%%', explode=explode,
                                           shadow=True, startangle=90)

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(11)

        for text in texts:
            text.set_fontsize(11)
            text.set_fontweight('bold')

        plt.title('System Performance Overview', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'performance_overview.png'),
                   dpi=300, bbox_inches='tight')
        plt.close()

    def _generate_antispoofing_chart(self, output_dir):
        """Generate anti-spoofing effectiveness chart"""
        if not self.results or not self.results.get('antispoofing_tests'):
            return

        detected = sum(1 for r in self.results['antispoofing_tests']
                      if r['detected_as_spoof'])
        missed = len(self.results['antispoofing_tests']) - detected

        labels = ['Detected', 'Missed']
        values = [detected, missed]
        colors = ['#2ecc71', '#e74c3c']
        explode = (0.1, 0)

        plt.figure(figsize=(8, 6))
        wedges, texts, autotexts = plt.pie(values, labels=labels, colors=colors,
                                           autopct='%1.1f%%', explode=explode,
                                           shadow=True, startangle=90)

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(12)

        for text in texts:
            text.set_fontsize(12)
            text.set_fontweight('bold')

        plt.title('Anti-Spoofing Detection Effectiveness', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'antispoofing_effectiveness.png'),
                   dpi=300, bbox_inches='tight')
        plt.close()

    def generate_html_report(self, output_path='data/results/security_report.html'):
        """
        Generate comprehensive HTML report

        Args:
            output_path: Path to save HTML report
        """
        if not self.results or not self.metrics:
            print("[-] No results loaded, cannot generate report")
            return

        print("[*] Generating HTML report...")

        # Generate charts first
        charts_dir = os.path.dirname(output_path) + '/charts'
        self.generate_charts(charts_dir)

        # Analyze vulnerabilities
        vulnerabilities = self._analyze_vulnerabilities()

        # Generate HTML content
        html_content = self._create_html_content(vulnerabilities)

        # Save report
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(html_content)

        print(f"[+] HTML report generated: {output_path}")

    def _analyze_vulnerabilities(self):
        """Analyze metrics and identify vulnerabilities"""
        vulnerabilities = []

        if self.metrics.get('FAR', 0) > 0.05:
            vulnerabilities.append({
                'severity': 'HIGH',
                'title': 'High False Acceptance Rate',
                'description': f"FAR of {self.metrics['FAR']:.2%} indicates system accepts imposters too frequently. "
                              "This is a critical security vulnerability.",
                'recommendation': 'Increase authentication threshold, implement multi-factor biometrics, '
                                'add liveness detection to all authentication attempts.'
            })

        if self.metrics.get('Attack_Success_Rate', 0) > 0.3:
            vulnerabilities.append({
                'severity': 'CRITICAL',
                'title': 'Vulnerable to Presentation Attacks',
                'description': f"Attack success rate of {self.metrics['Attack_Success_Rate']:.2%} is unacceptable for production deployment.",
                'recommendation': 'Implement comprehensive liveness detection, add texture analysis, '
                                'use challenge-response authentication, consider multi-modal biometrics.'
            })

        if self.metrics.get('FRR', 0) > 0.1:
            vulnerabilities.append({
                'severity': 'MEDIUM',
                'title': 'High False Rejection Rate',
                'description': f"FRR of {self.metrics['FRR']:.2%} may cause poor user experience.",
                'recommendation': 'Optimize matching thresholds, improve enrollment process with multiple samples, '
                                'add quality checks during capture.'
            })

        if self.metrics.get('AntiSpoof_Detection_Rate', 0) < 0.8:
            vulnerabilities.append({
                'severity': 'HIGH',
                'title': 'Insufficient Anti-Spoofing Protection',
                'description': f"Detection rate of {self.metrics.get('AntiSpoof_Detection_Rate', 0):.2%} is below acceptable threshold (80%).",
                'recommendation': 'Enhance liveness detection algorithms, add depth sensing, '
                                'implement active challenge tests, use neural network-based spoofing detection.'
            })

        return vulnerabilities

    def _create_html_content(self, vulnerabilities):
        """Create HTML report content"""
        total_tests = self.metrics.get('Total_Tests', {})
        total_count = sum(total_tests.values()) if total_tests else 0

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Biometric Security Assessment Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: #f5f7fa; color: #2c3e50; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%); color: white; padding: 40px; }}
        .header h1 {{ margin: 0 0 10px 0; font-size: 32px; }}
        .header p {{ margin: 5px 0; opacity: 0.9; }}
        .content {{ padding: 40px; }}
        .section {{ margin-bottom: 40px; }}
        .section h2 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-bottom: 20px; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }}
        .metric-box {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .metric-box.success {{ background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%); }}
        .metric-box.warning {{ background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); }}
        .metric-box.danger {{ background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); }}
        .metric-value {{ font-size: 42px; font-weight: bold; margin: 10px 0; }}
        .metric-label {{ font-size: 14px; opacity: 0.9; text-transform: uppercase; letter-spacing: 1px; }}
        .vulnerability {{ border-left: 5px solid; padding: 20px; margin: 20px 0; background: #fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-radius: 5px; }}
        .vulnerability.critical {{ border-color: #e74c3c; background: #fadbd8; }}
        .vulnerability.high {{ border-color: #e67e22; background: #fdebd0; }}
        .vulnerability.medium {{ border-color: #f39c12; background: #fcf3cf; }}
        .vulnerability h3 {{ margin-top: 0; color: #2c3e50; }}
        .vulnerability .severity {{ display: inline-block; padding: 5px 10px; border-radius: 3px; font-weight: bold; font-size: 12px; margin-bottom: 10px; }}
        .severity.critical {{ background: #e74c3c; color: white; }}
        .severity.high {{ background: #e67e22; color: white; }}
        .severity.medium {{ background: #f39c12; color: white; }}
        .chart {{ margin: 30px 0; text-align: center; }}
        .chart img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .info-box {{ background: #e8f4f8; border-left: 4px solid #3498db; padding: 20px; margin: 20px 0; border-radius: 5px; }}
        .recommendations {{ background: #e8f5e9; border-left: 4px solid #2ecc71; padding: 20px; margin: 20px 0; border-radius: 5px; }}
        .recommendations ul {{ margin: 10px 0; padding-left: 20px; }}
        .recommendations li {{ margin: 10px 0; line-height: 1.6; }}
        .footer {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #3498db; color: white; font-weight: bold; }}
        tr:hover {{ background: #f5f5f5; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Biometric Authentication Security Assessment</h1>
            <p>Comprehensive Vulnerability Analysis & Penetration Testing Report</p>
            <p>Face Recognition & Fingerprint System Evaluation</p>
            <p style="margin-top: 20px; opacity: 0.8;">Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="content">
            <div class="section">
                <h2>Executive Summary</h2>
                <p>This report presents the findings of a comprehensive security assessment of a biometric authentication system.
                The evaluation included systematic testing of presentation attacks (photo, video, 3D mask, degraded quality)
                and analysis of anti-spoofing defenses. The system was tested with <strong>{total_count}</strong> total security tests.</p>
            </div>

            <div class="section">
                <h2>Key Metrics</h2>
                <div class="metric-grid">
                    <div class="metric-box success">
                        <div class="metric-label">Genuine User Accuracy</div>
                        <div class="metric-value">{self.metrics.get('Genuine_Accuracy', 0):.1%}</div>
                    </div>
                    <div class="metric-box {'danger' if self.metrics.get('FAR', 0) > 0.05 else 'success'}">
                        <div class="metric-label">False Acceptance Rate</div>
                        <div class="metric-value">{self.metrics.get('FAR', 0):.2%}</div>
                    </div>
                    <div class="metric-box warning">
                        <div class="metric-label">False Rejection Rate</div>
                        <div class="metric-value">{self.metrics.get('FRR', 0):.2%}</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-label">Equal Error Rate</div>
                        <div class="metric-value">{self.metrics.get('EER', 0):.2%}</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>Test Coverage</h2>
                <table>
                    <tr>
                        <th>Test Category</th>
                        <th>Number of Tests</th>
                    </tr>
                    <tr>
                        <td>Genuine User Authentication</td>
                        <td>{total_tests.get('genuine', 0)}</td>
                    </tr>
                    <tr>
                        <td>Photo Presentation Attacks</td>
                        <td>{total_tests.get('photo_attacks', 0)}</td>
                    </tr>
                    <tr>
                        <td>3D Mask Attacks</td>
                        <td>{total_tests.get('mask_attacks', 0)}</td>
                    </tr>
                    <tr>
                        <td>Degraded Quality Attacks</td>
                        <td>{total_tests.get('degraded_attacks', 0)}</td>
                    </tr>
                    <tr>
                        <td>Anti-Spoofing Tests</td>
                        <td>{total_tests.get('antispoofing', 0)}</td>
                    </tr>
                    <tr style="font-weight: bold; background: #ecf0f1;">
                        <td>Total Security Tests</td>
                        <td>{total_count}</td>
                    </tr>
                </table>
            </div>

            <div class="section">
                <h2>Attack Success Rates</h2>
                <div class="chart">
                    <img src="charts/attack_success_rates.png" alt="Attack Success Rates">
                </div>
                <div class="info-box">
                    <strong>Analysis:</strong> The chart above shows how effectively different types of presentation attacks
                    fooled the authentication system. Lower values indicate better security.
                </div>
            </div>

            <div class="section">
                <h2>System Error Rates</h2>
                <div class="chart">
                    <img src="charts/error_rates.png" alt="Error Rates">
                </div>
            </div>

            <div class="section">
                <h2>Performance Overview</h2>
                <div class="chart">
                    <img src="charts/performance_overview.png" alt="Performance Overview">
                </div>
            </div>

            <div class="section">
                <h2>Vulnerabilities Discovered</h2>
                {''.join([f'''
                <div class="vulnerability {vuln['severity'].lower()}">
                    <span class="severity {vuln['severity'].lower()}">{vuln['severity']}</span>
                    <h3>{vuln['title']}</h3>
                    <p><strong>Description:</strong> {vuln['description']}</p>
                    <p><strong>Recommendation:</strong> {vuln['recommendation']}</p>
                </div>
                ''' for vuln in vulnerabilities])}
            </div>

            <div class="section">
                <h2>Security Recommendations</h2>
                <div class="recommendations">
                    <h3>Immediate Actions Required:</h3>
                    <ul>
                        <li><strong>Implement Multi-Factor Biometrics:</strong> Combine face + fingerprint + behavioral biometrics for enhanced security</li>
                        <li><strong>Deploy Active Liveness Detection:</strong> Challenge-response tests, blink detection, head movement analysis</li>
                        <li><strong>Add Texture Analysis:</strong> Implement LBP and deep learning-based texture classifiers to detect printed photos and screen replays</li>
                        <li><strong>Use Depth Sensors:</strong> Integrate 3D cameras or stereo vision for depth verification against mask attacks</li>
                        <li><strong>Neural Network Anti-Spoofing:</strong> Train CNN models on attack datasets for robust spoofing detection</li>
                        <li><strong>Regular Security Audits:</strong> Conduct quarterly penetration testing and vulnerability assessments</li>
                        <li><strong>Continuous Monitoring:</strong> Implement anomaly detection and real-time threat monitoring</li>
                    </ul>
                </div>
            </div>

            <div class="section">
                <h2>Australian Privacy Compliance</h2>
                <div class="info-box">
                    <h3>Privacy Act 1988 Compliance Requirements:</h3>
                    <p>Biometric data is classified as <strong>sensitive information</strong> under the Privacy Act 1988.
                    Organizations deploying this system must ensure:</p>
                    <ul>
                        <li><strong>Consent:</strong> Obtain explicit, informed consent before collecting biometric data</li>
                        <li><strong>Security:</strong> Implement AES-256 encryption for biometric templates at rest and TLS 1.3 for data in transit</li>
                        <li><strong>Retention:</strong> Implement secure deletion procedures and data retention policies</li>
                        <li><strong>Breach Notification:</strong> Report notifiable data breaches to OAIC within 30 days</li>
                        <li><strong>Privacy Impact Assessment:</strong> Conduct PIAs before deployment and after major changes</li>
                        <li><strong>Third-Party Compliance:</strong> Ensure cloud providers and vendors comply with Australian privacy laws</li>
                    </ul>
                    <p><strong>Reference:</strong> Office of the Australian Information Commissioner (OAIC) -
                    <a href="https://www.oaic.gov.au/" target="_blank">www.oaic.gov.au</a></p>
                </div>
            </div>

            <div class="section">
                <h2>Conclusion</h2>
                <p>This security assessment demonstrates the importance of comprehensive anti-spoofing measures in biometric authentication systems.
                While face and fingerprint recognition provide convenient authentication, they are vulnerable to presentation attacks
                without proper liveness detection and multi-factor approaches.</p>

                <p>The findings underscore the need for <strong>layered security defenses</strong> combining multiple biometric modalities,
                active liveness detection, texture analysis, depth sensing, and continuous monitoring for emerging threats such as
                deepfakes and synthetic biometrics.</p>

                <p><strong>Security Posture:</strong> {'NEEDS IMPROVEMENT' if self.metrics.get('FAR', 0) > 0.1 else 'ACCEPTABLE' if self.metrics.get('FAR', 0) > 0.05 else 'GOOD'}</p>
            </div>
        </div>

        <div class="footer">
            <p>Biometric Security Research Project</p>
            <p>Generated with Python, OpenCV, DeepFace, and Matplotlib</p>
            <p>For research and educational purposes</p>
        </div>
    </div>
</body>
</html>"""

        return html

    def generate_executive_summary(self):
        """Generate executive summary text"""
        if not self.metrics:
            return "No metrics available for executive summary"

        far = self.metrics.get('FAR', 0)
        security_posture = 'POOR' if far > 0.1 else 'MODERATE' if far > 0.05 else 'GOOD'

        summary = f"""
BIOMETRIC SECURITY ASSESSMENT - EXECUTIVE SUMMARY
{'='*70}

Assessment Date: {datetime.now().strftime('%Y-%m-%d')}
System: Face Recognition + Fingerprint Authentication
Security Posture: {security_posture}

KEY FINDINGS:
{'-'*70}
False Acceptance Rate (FAR):        {self.metrics.get('FAR', 0):.2%}
False Rejection Rate (FRR):         {self.metrics.get('FRR', 0):.2%}
Equal Error Rate (EER):              {self.metrics.get('EER', 0):.2%}
Genuine User Accuracy:               {self.metrics.get('Genuine_Accuracy', 0):.2%}
Attack Success Rate:                 {self.metrics.get('Attack_Success_Rate', 0):.2%}
Anti-Spoofing Detection Rate:        {self.metrics.get('AntiSpoof_Detection_Rate', 0):.2%}

VULNERABILITIES IDENTIFIED:
{'-'*70}
1. Photo Presentation Attacks:       {'HIGH RISK' if self.metrics.get('Attack_Success_Rate', 0) > 0.3 else 'MODERATE RISK'}
2. 3D Mask Attacks:                  {'HIGH RISK' if self.metrics.get('Attack_Success_Rate', 0) > 0.2 else 'MODERATE RISK'}
3. Liveness Detection:               {'NOT IMPLEMENTED' if self.metrics.get('AntiSpoof_Detection_Rate', 0) < 0.5 else 'BASIC IMPLEMENTATION'}
4. Multi-Factor Authentication:      NOT IMPLEMENTED

RECOMMENDATIONS:
{'-'*70}
IMMEDIATE:
1. Implement active liveness detection (blink, head movement)
2. Add texture analysis for photo/screen detection
3. Deploy challenge-response authentication

SHORT-TERM:
4. Integrate depth sensors or stereo cameras
5. Train neural network anti-spoofing models
6. Implement multi-modal biometrics

LONG-TERM:
7. Regular security audits and penetration testing
8. Continuous monitoring and anomaly detection
9. Research emerging attack vectors (deepfakes, synthetic biometrics)

COMPLIANCE NOTES (Australian Context):
{'-'*70}
- Privacy Act 1988: Biometric data is sensitive information
- OAIC Guidelines: Requires explicit consent and secure storage
- Notifiable Data Breaches: System vulnerabilities may be reportable
- Encryption: Implement AES-256 at rest, TLS 1.3 in transit
- Regular PIAs required before deployment

This assessment demonstrates the critical importance of robust anti-spoofing
measures in biometric authentication systems deployed in Australian enterprises,
government agencies, and financial institutions.
{'='*70}
"""

        return summary
