"""
Enhanced security reporting with interactive dashboards.
Generates professional HTML reports with Plotly visualizations.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from jinja2 import Template
from utils.logger import get_logger

logger = get_logger(__name__)


class EnhancedReportGenerator:
    """
    Generate enhanced interactive security reports
    """

    def __init__(self, results_file: Optional[str] = None, results_data: Optional[Dict] = None):
        """
        Initialize enhanced report generator

        Args:
            results_file: Path to results JSON file
            results_data: Results data dictionary (if not loading from file)
        """
        self.results = None

        if results_file and os.path.exists(results_file):
            with open(results_file, 'r') as f:
                self.results = json.load(f)
        elif results_data:
            self.results = results_data
        else:
            logger.warning("No results provided to report generator")

        if not PLOTLY_AVAILABLE:
            logger.warning("Plotly not available, falling back to matplotlib")

    def generate_interactive_dashboard(self, output_path: str):
        """
        Generate interactive HTML dashboard

        Args:
            output_path: Path to save HTML report
        """
        if not self.results:
            logger.error("No results to generate report from")
            return

        logger.info(f"Generating enhanced interactive report: {output_path}")

        # Create visualizations
        visualizations = {}

        if PLOTLY_AVAILABLE:
            visualizations['metrics_gauge'] = self._create_metrics_gauges()
            visualizations['attack_success_chart'] = self._create_attack_success_chart()
            visualizations['confusion_matrix'] = self._create_confusion_matrix()
            visualizations['timeline'] = self._create_test_timeline()
            visualizations['antispoofing_breakdown'] = self._create_antispoofing_breakdown()

        # Generate HTML report
        html_content = self._generate_html(visualizations)

        # Save report
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(html_content)

        logger.info(f"Enhanced report saved to: {output_path}")

    def _create_metrics_gauges(self) -> str:
        """Create gauge charts for key metrics"""
        if not self.results or 'metrics' not in self.results:
            return ""

        metrics = self.results['metrics']

        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=('FAR (Lower is Better)', 'FRR (Lower is Better)', 'EER (Lower is Better)',
                          'Genuine Accuracy', 'Anti-Spoof Detection', 'Overall Security'),
            specs=[[{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}],
                   [{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}]]
        )

        # FAR Gauge
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=metrics.get('FAR', 0) * 100,
            title={'text': "FAR (%)"},
            delta={'reference': 1.0},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkred" if metrics.get('FAR', 0) > 0.05 else "green"},
                'steps': [
                    {'range': [0, 1], 'color': "lightgreen"},
                    {'range': [1, 5], 'color': "yellow"},
                    {'range': [5, 100], 'color': "lightcoral"}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 5}
            }
        ), row=1, col=1)

        # FRR Gauge
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=metrics.get('FRR', 0) * 100,
            title={'text': "FRR (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkred" if metrics.get('FRR', 0) > 0.1 else "green"},
                'steps': [
                    {'range': [0, 5], 'color': "lightgreen"},
                    {'range': [5, 10], 'color': "yellow"},
                    {'range': [10, 100], 'color': "lightcoral"}
                ]
            }
        ), row=1, col=2)

        # EER Gauge
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=metrics.get('EER', 0) * 100,
            title={'text': "EER (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkred" if metrics.get('EER', 0) > 0.1 else "green"},
                'steps': [
                    {'range': [0, 5], 'color': "lightgreen"},
                    {'range': [5, 10], 'color': "yellow"},
                    {'range': [10, 100], 'color': "lightcoral"}
                ]
            }
        ), row=1, col=3)

        # Genuine Accuracy
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=metrics.get('Genuine_Accuracy', 0) * 100,
            title={'text': "Genuine (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "green" if metrics.get('Genuine_Accuracy', 0) > 0.95 else "orange"},
                'steps': [
                    {'range': [0, 90], 'color': "lightcoral"},
                    {'range': [90, 95], 'color': "yellow"},
                    {'range': [95, 100], 'color': "lightgreen"}
                ]
            }
        ), row=2, col=1)

        # Anti-Spoofing Detection
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=metrics.get('AntiSpoof_Detection_Rate', 0) * 100,
            title={'text': "Anti-Spoof (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "green" if metrics.get('AntiSpoof_Detection_Rate', 0) > 0.8 else "orange"},
                'steps': [
                    {'range': [0, 70], 'color': "lightcoral"},
                    {'range': [70, 85], 'color': "yellow"},
                    {'range': [85, 100], 'color': "lightgreen"}
                ]
            }
        ), row=2, col=2)

        # Overall Security Score
        overall_score = (
            (1 - metrics.get('FAR', 1)) * 0.3 +
            (1 - metrics.get('FRR', 1)) * 0.2 +
            (1 - metrics.get('EER', 1)) * 0.2 +
            metrics.get('AntiSpoof_Detection_Rate', 0) * 0.3
        ) * 100

        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=overall_score,
            title={'text': "Security Score"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "green" if overall_score > 80 else "orange"},
                'steps': [
                    {'range': [0, 60], 'color': "lightcoral"},
                    {'range': [60, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "lightgreen"}
                ]
            }
        ), row=2, col=3)

        fig.update_layout(
            height=600,
            title_text="<b>Security Metrics Dashboard</b>",
            showlegend=False
        )

        return fig.to_html(include_plotlyjs='cdn', div_id='metrics_gauges')

    def _create_attack_success_chart(self) -> str:
        """Create bar chart showing attack success rates"""
        if not self.results:
            return ""

        attack_data = []

        for attack_type in ['photo_attacks', 'mask_attacks', 'degraded_attacks']:
            if attack_type in self.results and self.results[attack_type]:
                fooled = sum(1 for r in self.results[attack_type] if r.get('fooled_system', False))
                total = len(self.results[attack_type])
                success_rate = (fooled / total * 100) if total > 0 else 0

                attack_data.append({
                    'Attack Type': attack_type.replace('_', ' ').title(),
                    'Success Rate (%)': success_rate,
                    'Total Tests': total
                })

        if not attack_data:
            return ""

        import pandas as pd
        df = pd.DataFrame(attack_data)

        fig = go.Figure(data=[
            go.Bar(
                x=df['Attack Type'],
                y=df['Success Rate (%)'],
                text=df['Success Rate (%)'].round(1),
                textposition='auto',
                marker=dict(
                    color=df['Success Rate (%)'],
                    colorscale='RdYlGn_r',  # Red for high, green for low
                    showscale=True,
                    colorbar=dict(title="Success Rate (%)")
                ),
                hovertemplate='<b>%{x}</b><br>Success Rate: %{y:.1f}%<br>Total Tests: %{customdata}<extra></extra>',
                customdata=df['Total Tests']
            )
        ])

        fig.update_layout(
            title="<b>Attack Success Rates</b> (Lower is Better)",
            xaxis_title="Attack Type",
            yaxis_title="Success Rate (%)",
            yaxis=dict(range=[0, 100]),
            height=400,
            hovermode='x'
        )

        return fig.to_html(include_plotlyjs=False, div_id='attack_success')

    def _create_confusion_matrix(self) -> str:
        """Create confusion matrix for genuine vs attack detection"""
        if not self.results or 'genuine_tests' not in self.results:
            return ""

        # Calculate true positives, false positives, etc.
        genuine_tests = self.results.get('genuine_tests', [])
        attack_tests = (
            self.results.get('photo_attacks', []) +
            self.results.get('mask_attacks', []) +
            self.results.get('degraded_attacks', [])
        )

        tp = sum(1 for r in genuine_tests if r.get('authenticated', False))  # True Positive
        fn = sum(1 for r in genuine_tests if not r.get('authenticated', False))  # False Negative
        tn = sum(1 for r in attack_tests if not r.get('fooled_system', False))  # True Negative
        fp = sum(1 for r in attack_tests if r.get('fooled_system', False))  # False Positive

        z = [[tn, fp], [fn, tp]]
        x = ['Predicted: Attack', 'Predicted: Genuine']
        y = ['Actual: Attack', 'Actual: Genuine']

        fig = go.Figure(data=go.Heatmap(
            z=z,
            x=x,
            y=y,
            text=z,
            texttemplate='<b>%{text}</b>',
            textfont={"size": 20},
            colorscale='Blues',
            showscale=True
        ))

        fig.update_layout(
            title="<b>Confusion Matrix</b>",
            xaxis_title="Prediction",
            yaxis_title="Actual",
            height=400
        )

        return fig.to_html(include_plotlyjs=False, div_id='confusion_matrix')

    def _create_test_timeline(self) -> str:
        """Create timeline of test results"""
        # Simplified timeline showing test counts
        if not self.results:
            return ""

        test_summary = {
            'Genuine Tests': len(self.results.get('genuine_tests', [])),
            'Photo Attacks': len(self.results.get('photo_attacks', [])),
            'Mask Attacks': len(self.results.get('mask_attacks', [])),
            'Degraded Attacks': len(self.results.get('degraded_attacks', [])),
            'Anti-Spoofing Tests': len(self.results.get('antispoofing_tests', []))
        }

        fig = go.Figure(data=[
            go.Bar(
                x=list(test_summary.keys()),
                y=list(test_summary.values()),
                marker_color='lightblue',
                text=list(test_summary.values()),
                textposition='auto'
            )
        ])

        fig.update_layout(
            title="<b>Test Volume Summary</b>",
            xaxis_title="Test Category",
            yaxis_title="Number of Tests",
            height=350
        )

        return fig.to_html(include_plotlyjs=False, div_id='test_timeline')

    def _create_antispoofing_breakdown(self) -> str:
        """Create breakdown of anti-spoofing check results"""
        if not self.results or 'antispoofing_tests' not in self.results:
            return ""

        antispoofing_tests = self.results['antispoofing_tests']

        if not antispoofing_tests:
            return ""

        # Aggregate results
        check_results = {}
        for test in antispoofing_tests:
            if 'checks' in test:
                for check_name, check_data in test['checks'].items():
                    if check_name not in check_results:
                        check_results[check_name] = {'passed': 0, 'failed': 0}

                    # Determine if check detected spoof
                    detected = (
                        check_data.get('is_real', False) == False or
                        check_data.get('is_3d', False) == False or
                        check_data.get('is_live', False) == False
                    )

                    if detected:
                        check_results[check_name]['passed'] += 1
                    else:
                        check_results[check_name]['failed'] += 1

        if not check_results:
            return ""

        checks = list(check_results.keys())
        passed = [check_results[c]['passed'] for c in checks]
        failed = [check_results[c]['failed'] for c in checks]

        fig = go.Figure(data=[
            go.Bar(name='Detected', x=checks, y=passed, marker_color='green'),
            go.Bar(name='Missed', x=checks, y=failed, marker_color='red')
        ])

        fig.update_layout(
            title="<b>Anti-Spoofing Check Performance</b>",
            xaxis_title="Check Type",
            yaxis_title="Count",
            barmode='stack',
            height=400
        )

        return fig.to_html(include_plotlyjs=False, div_id='antispoofing_breakdown')

    def _generate_html(self, visualizations: Dict[str, str]) -> str:
        """Generate complete HTML report"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        metrics = self.results.get('metrics', {}) if self.results else {}
        test_metadata = self.results.get('test_metadata', {}) if self.results else {}

        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Biometric Security Assessment Report</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        .content {
            padding: 40px;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            color: #1e3c72;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .metric-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .metric-card h3 {
            margin: 0;
            font-size: 0.9em;
            color: #555;
            text-transform: uppercase;
        }
        .metric-card .value {
            font-size: 2.5em;
            font-weight: bold;
            color: #1e3c72;
            margin: 10px 0;
        }
        .metric-card .label {
            font-size: 0.85em;
            color: #777;
        }
        .status-good { color: #27ae60; }
        .status-warning { color: #f39c12; }
        .status-bad { color: #e74c3c; }
        .footer {
            background: #f5f7fa;
            padding: 20px 40px;
            text-align: center;
            color: #777;
            font-size: 0.9em;
        }
        .chart-container {
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Biometric Security Assessment Report</h1>
            <p>Generated on {{ timestamp }}</p>
            <p>Version {{ version }}</p>
        </div>

        <div class="content">
            <div class="section">
                <h2>📊 Executive Summary</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>False Acceptance Rate</h3>
                        <div class="value {{ 'status-good' if far < 0.01 else ('status-warning' if far < 0.05 else 'status-bad') }}">
                            {{ "%.2f"|format(far * 100) }}%
                        </div>
                        <div class="label">Imposters Accepted</div>
                    </div>
                    <div class="metric-card">
                        <h3>False Rejection Rate</h3>
                        <div class="value {{ 'status-good' if frr < 0.05 else ('status-warning' if frr < 0.1 else 'status-bad') }}">
                            {{ "%.2f"|format(frr * 100) }}%
                        </div>
                        <div class="label">Genuine Users Rejected</div>
                    </div>
                    <div class="metric-card">
                        <h3>Overall Accuracy</h3>
                        <div class="value status-good">
                            {{ "%.2f"|format(accuracy * 100) }}%
                        </div>
                        <div class="label">Genuine User Authentication</div>
                    </div>
                    <div class="metric-card">
                        <h3>Anti-Spoof Detection</h3>
                        <div class="value {{ 'status-good' if antispoof > 0.85 else ('status-warning' if antispoof > 0.7 else 'status-bad') }}">
                            {{ "%.2f"|format(antispoof * 100) }}%
                        </div>
                        <div class="label">Attacks Detected</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>📈 Performance Metrics</h2>
                <div class="chart-container">
                    {{ metrics_gauge|safe }}
                </div>
            </div>

            <div class="section">
                <h2>🎯 Attack Analysis</h2>
                <div class="chart-container">
                    {{ attack_success_chart|safe }}
                </div>
                <div class="chart-container">
                    {{ confusion_matrix|safe }}
                </div>
            </div>

            <div class="section">
                <h2>🛡️ Defense Effectiveness</h2>
                <div class="chart-container">
                    {{ antispoofing_breakdown|safe }}
                </div>
            </div>

            <div class="section">
                <h2>📋 Test Summary</h2>
                <div class="chart-container">
                    {{ timeline|safe }}
                </div>
            </div>

            <div class="section">
                <h2>💡 Recommendations</h2>
                <ul>
                    {% if far > 0.05 %}
                    <li class="status-bad"><strong>Critical:</strong> High False Acceptance Rate ({{ "%.2f"|format(far * 100) }}%). Strengthen authentication threshold.</li>
                    {% endif %}
                    {% if frr > 0.1 %}
                    <li class="status-warning"><strong>Warning:</strong> High False Rejection Rate ({{ "%.2f"|format(frr * 100) }}%). May impact user experience.</li>
                    {% endif %}
                    {% if antispoof < 0.8 %}
                    <li class="status-bad"><strong>Critical:</strong> Low anti-spoofing detection rate. Implement additional liveness checks.</li>
                    {% endif %}
                    {% if far < 0.01 and frr < 0.05 and antispoof > 0.85 %}
                    <li class="status-good"><strong>Excellent:</strong> System shows strong security metrics across all categories.</li>
                    {% endif %}
                    <li>Consider implementing multi-factor authentication for critical applications.</li>
                    <li>Regular security audits and updates are recommended.</li>
                    <li>Ensure compliance with local privacy regulations (Privacy Act 1988 for Australian deployments).</li>
                </ul>
            </div>
        </div>

        <div class="footer">
            <p>Biometric Security Research System v{{ version }}</p>
            <p>This report is for security research and authorized testing purposes only.</p>
            <p>© {{ year }} Biometric Security Research | Compliant with Australian Privacy Act 1988</p>
        </div>
    </div>
</body>
</html>
"""

        template = Template(html_template)

        return template.render(
            timestamp=timestamp,
            version='2.0.0',
            year=datetime.now().year,
            far=metrics.get('FAR', 0),
            frr=metrics.get('FRR', 0),
            accuracy=metrics.get('Genuine_Accuracy', 0),
            antispoof=metrics.get('AntiSpoof_Detection_Rate', 0),
            metrics_gauge=visualizations.get('metrics_gauge', ''),
            attack_success_chart=visualizations.get('attack_success_chart', ''),
            confusion_matrix=visualizations.get('confusion_matrix', ''),
            timeline=visualizations.get('timeline', ''),
            antispoofing_breakdown=visualizations.get('antispoofing_breakdown', '')
        )
