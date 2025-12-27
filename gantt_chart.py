"""
Gantt Chart and Visualization Functions for JSP
Uses Plotly with green/white color scheme
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Tuple, Optional
from jsp_model import Schedule, JSPProblem


# Modern color palette - Diverse colors for jobs
JOB_COLORS = [
    "#2E7D32",  # Green (principal)
    "#1976D2",  # Blue
    "#D32F2F",  # Red
    "#F57C00",  # Orange
    "#7B1FA2",  # Purple
    "#0097A7",  # Cyan
    "#C2185B",  # Pink
    "#5D4037",  # Brown
    "#455A64",  # Blue Grey
    "#689F38",  # Light Green
    "#0288D1",  # Light Blue
    "#E64A19",  # Deep Orange
    "#512DA8",  # Deep Purple
    "#00796B",  # Teal
    "#F44336",  # Bright Red
]

GREEN_PALETTE = {
    "dark": "#1B5E20",
    "primary": "#2E7D32",
    "medium": "#4CAF50",
    "light": "#66BB6A",
    "lighter": "#81C784",
    "lightest": "#C8E6C9",
    "background": "#F1F8E9"
}


def get_job_color(job_id: int, n_jobs: int) -> str:
    """Get unique color for each job - vibrant and distinctive"""
    return JOB_COLORS[job_id % len(JOB_COLORS)]


def create_gantt_chart(schedule: Schedule, problem: JSPProblem,
                       title: str = "Job Shop Schedule - Gantt Chart") -> go.Figure:
    """
    Create interactive Gantt chart using Plotly

    Args:
        schedule: Solution schedule
        problem: Problem instance
        title: Chart title

    Returns:
        Plotly Figure
    """

    # Prepare data for Gantt chart
    gantt_data = []

    for (job_id, op_idx), (start, end) in schedule.operation_times.items():
        job = problem.get_job(job_id)
        operation = job.operations[op_idx]
        machine_id = operation.machine_id

        gantt_data.append({
            'Machine': f'M{machine_id}',
            'Job': f'J{job_id}',
            'Start': start,
            'Finish': end,
            'Duration': end - start,
            'Operation': op_idx,
            'job_id_num': job_id
        })

    df = pd.DataFrame(gantt_data)

    # Sort by machine and start time
    df = df.sort_values(['Machine', 'Start'])

    # Create figure
    fig = go.Figure()

    # Add bars for each operation with better styling
    for _, row in df.iterrows():
        color = get_job_color(row['job_id_num'], problem.n_jobs)

        fig.add_trace(go.Bar(
            x=[row['Duration']],
            y=[row['Machine']],
            base=[row['Start']],
            orientation='h',
            name=row['Job'],
            marker=dict(
                color=color,
                line=dict(color='rgba(255,255,255,0.8)', width=2),
                opacity=0.85
            ),
            text=f"{row['Job']}",
            textposition='inside',
            textfont=dict(color='white', size=12, family='Arial Black'),
            hovertemplate=(
                f"<b>{row['Job']} - Op{row['Operation']}</b><br>" +
                f"Machine: {row['Machine']}<br>" +
                f"Start: {row['Start']}<br>" +
                f"End: {row['Finish']}<br>" +
                f"Duration: {row['Duration']}<br>" +
                "<extra></extra>"
            ),
            showlegend=False
        ))

    # Add vertical line at makespan
    makespan = schedule.makespan
    fig.add_vline(
        x=makespan,
        line_dash="dash",
        line_color="#FF5722",
        line_width=3,
        annotation_text=f"Makespan: {makespan}",
        annotation_position="top",
        annotation_font=dict(size=14, color="#FF5722", family="Arial Black")
    )

    # Add legend for jobs
    for job_id in range(problem.n_jobs):
        color = get_job_color(job_id, problem.n_jobs)
        fig.add_trace(go.Scatter(
            x=[None], y=[None],
            mode='markers',
            marker=dict(size=15, color=color, symbol='square'),
            name=f'Job {job_id}',
            showlegend=True
        ))

    # Update layout
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': GREEN_PALETTE["primary"], 'family': 'Arial Black'}
        },
        xaxis_title="Temps (unités)",
        yaxis_title="Machines",
        barmode='overlay',
        height=max(450, problem.n_machines * 70),
        plot_bgcolor='#FAFAFA',
        paper_bgcolor='white',
        font=dict(color='#333333', size=12),
        xaxis=dict(
            showgrid=True,
            gridcolor='#E0E0E0',
            gridwidth=1,
            zeroline=True,
            zerolinecolor='#BDBDBD',
            zerolinewidth=2,
            title_font=dict(size=14, family='Arial', color=GREEN_PALETTE["primary"])
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#E0E0E0',
            gridwidth=1,
            title_font=dict(size=14, family='Arial', color=GREEN_PALETTE["primary"])
        ),
        hovermode='closest',
        legend=dict(
            title=dict(text="Jobs", font=dict(size=14, family='Arial Black', color=GREEN_PALETTE["primary"])),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor=GREEN_PALETTE["primary"],
            borderwidth=2,
            font=dict(size=12)
        )
    )

    return fig


def create_convergence_plot(convergence_history: List[Tuple[int, int, float]],
                           bks: Optional[int] = None,
                           problem_name: str = "") -> go.Figure:
    """
    Create convergence plot showing SA progress

    Args:
        convergence_history: List of (iteration, makespan, temperature)
        bks: Best-Known Solution (optional)
        problem_name: Instance name for title

    Returns:
        Plotly Figure
    """

    # Extract data
    iterations = [h[0] for h in convergence_history]
    makespans = [h[1] for h in convergence_history]
    temperatures = [h[2] for h in convergence_history]

    # Calculate best-so-far
    best_so_far = []
    current_best = float('inf')
    for ms in makespans:
        if ms < current_best:
            current_best = ms
        best_so_far.append(current_best)

    # Create figure with secondary y-axis
    fig = go.Figure()

    # Add best makespan line with gradient effect
    fig.add_trace(go.Scatter(
        x=iterations,
        y=best_so_far,
        mode='lines',
        name='Meilleur Makespan',
        line=dict(color=GREEN_PALETTE["primary"], width=4),
        fill='tozeroy',
        fillcolor='rgba(46, 125, 50, 0.1)',
        hovertemplate="<b>Iteration: %{x}</b><br>Meilleur: %{y}<extra></extra>"
    ))

    # Add current makespan (blue, more visible)
    fig.add_trace(go.Scatter(
        x=iterations,
        y=makespans,
        mode='lines',
        name='Makespan Actuel',
        line=dict(color='#1976D2', width=2, dash='dot'),
        opacity=0.6,
        hovertemplate="<b>Iteration: %{x}</b><br>Actuel: %{y}<extra></extra>"
    ))

    # Add BKS line if available
    if bks is not None:
        fig.add_hline(
            y=bks,
            line_dash="dash",
            line_color="#FF5722",
            line_width=3,
            annotation_text=f"BKS: {bks}",
            annotation_position="right",
            annotation_font=dict(size=13, color="#FF5722", family="Arial Black")
        )

    # Add annotations
    initial_ms = best_so_far[0]
    final_ms = best_so_far[-1]
    improvement = ((initial_ms - final_ms) / initial_ms * 100) if initial_ms > 0 else 0

    fig.add_annotation(
        x=0,
        y=initial_ms,
        text=f"Initial: {initial_ms}",
        showarrow=True,
        arrowhead=2,
        ax=40,
        ay=-40,
        bgcolor=GREEN_PALETTE["lightest"],
        bordercolor=GREEN_PALETTE["primary"]
    )

    fig.add_annotation(
        x=iterations[-1],
        y=final_ms,
        text=f"Final: {final_ms}<br>({improvement:.1f}% improvement)",
        showarrow=True,
        arrowhead=2,
        ax=-40,
        ay=40,
        bgcolor=GREEN_PALETTE["lightest"],
        bordercolor=GREEN_PALETTE["primary"]
    )

    # Update layout
    title_text = f"Courbe de Convergence - {problem_name}" if problem_name else "Courbe de Convergence"
    fig.update_layout(
        title={
            'text': title_text,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': GREEN_PALETTE["primary"], 'family': 'Arial Black'}
        },
        xaxis_title="Itération",
        yaxis_title="Makespan",
        height=550,
        plot_bgcolor='#FAFAFA',
        paper_bgcolor='white',
        font=dict(color='#333333', size=12),
        xaxis=dict(
            showgrid=True,
            gridcolor='#E0E0E0',
            gridwidth=1,
            title_font=dict(size=14, family='Arial', color=GREEN_PALETTE["primary"])
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#E0E0E0',
            gridwidth=1,
            title_font=dict(size=14, family='Arial', color=GREEN_PALETTE["primary"])
        ),
        hovermode='x unified',
        legend=dict(
            title=dict(text="", font=dict(size=13, family='Arial Black')),
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor=GREEN_PALETTE["primary"],
            borderwidth=2,
            font=dict(size=12)
        )
    )

    return fig


def create_simple_gantt_text(schedule: Schedule, problem: JSPProblem) -> str:
    """
    Create simple text-based Gantt chart (similar to Metod_exact.py output)

    Returns:
        String representation of Gantt chart
    """
    makespan = schedule.makespan
    lines = []

    lines.append(f"\nOPTIMAL MAKESPAN: {makespan}\n")

    # Display operation details per job
    for job in problem.jobs:
        lines.append(f"\nJob {job.job_id}:")
        for op_idx, operation in enumerate(job.operations):
            times = schedule.get_operation_time(job.job_id, op_idx)
            if times:
                start, end = times
                lines.append(
                    f"  Op {op_idx+1}: M{operation.machine_id}({operation.duration}) -> "
                    f"Start: {start}, End: {end}"
                )

    # Display timeline per machine
    lines.append(f"\n{'='*60}")
    lines.append("TIMELINE PER MACHINE:")
    lines.append('='*60)

    for machine_id in range(problem.n_machines):
        # Get all operations on this machine
        machine_ops = []
        for (job_id, op_idx), (start, end) in schedule.operation_times.items():
            job = problem.get_job(job_id)
            if job.operations[op_idx].machine_id == machine_id:
                machine_ops.append((start, end, job_id, op_idx))

        machine_ops.sort()  # Sort by start time

        # Create timeline string
        timeline = ['.' for _ in range(makespan)]
        for start, end, job_id, _ in machine_ops:
            for t in range(start, end):
                timeline[t] = str(job_id)

        lines.append(f"\nM{machine_id}: |{''.join(timeline)}|")

    return '\n'.join(lines)
