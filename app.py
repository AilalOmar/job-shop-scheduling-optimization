"""
Job Shop Scheduler - Streamlit Application
Comparison: Greedy Algorithm vs Simulated Annealing
"""

import streamlit as st
import pandas as pd
import json
from jsp_model import JSPProblem, Job, Operation
from simulated_annealing import SimulatedAnnealingSolver
from cp_sat_solver import CPSatSolver
from gantt_chart import create_gantt_chart

# Page configuration
st.set_page_config(
    page_title="Job Shop Scheduler - Algorithmes de Résolution",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Modern vibrant multi-color theme
st.markdown("""
<style>
    /* Background - Vibrant colorful gradient */
    .main {
        background: linear-gradient(135deg,
            #E3F2FD 0%,
            #FFFFFF 20%,
            #FFF3E0 40%,
            #FFFFFF 60%,
            #F3E5F5 80%,
            #FFFFFF 100%);
    }

    /* Primary buttons - Vibrant blue/purple gradient */
    .stButton>button {
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 50%, #1565C0 100%);
        color: white;
        border: none;
        border-radius: 14px;
        padding: 14px 32px;
        font-weight: 700;
        font-size: 17px;
        box-shadow: 0 6px 12px rgba(33, 150, 243, 0.4);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1976D2 0%, #0D47A1 50%, #01579B 100%);
        box-shadow: 0 8px 16px rgba(33, 150, 243, 0.5);
        transform: translateY(-3px);
    }

    /* Headers - Vibrant varied colors */
    h1 {
        background: linear-gradient(90deg, #1565C0 0%, #7B1FA2 50%, #C2185B 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-family: 'Arial Black', sans-serif;
        font-weight: 900;
        text-shadow: 3px 3px 6px rgba(21, 101, 192, 0.2);
        padding-bottom: 12px;
    }
    h2 {
        color: #F57C00;
        font-family: 'Arial', sans-serif;
        font-weight: 700;
        border-left: 6px solid #FF9800;
        padding-left: 18px;
        margin-top: 25px;
        text-shadow: 2px 2px 4px rgba(245, 124, 0, 0.15);
    }
    h3 {
        color: #7B1FA2;
        font-weight: 700;
        margin-top: 18px;
        text-shadow: 1px 1px 3px rgba(123, 31, 162, 0.15);
    }

    /* Metrics - Vibrant gradient text */
    [data-testid="stMetricValue"] {
        font-size: 36px;
        font-weight: 900;
        background: linear-gradient(135deg, #2196F3 0%, #7B1FA2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Sidebar - Colorful gradient */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg,
            #E3F2FD 0%,
            #F3E5F5 33%,
            #FFF3E0 66%,
            #E8F5E9 100%);
        border-right: 4px solid;
        border-image: linear-gradient(180deg, #2196F3, #7B1FA2, #FF9800, #4CAF50) 1;
    }

    /* Inputs - Blue/purple focus */
    .stNumberInput > div > div > input,
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 2px solid #BDBDBD;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    .stNumberInput > div > div > input:focus,
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #2196F3;
        box-shadow: 0 0 0 4px rgba(33, 150, 243, 0.15);
    }

    /* Sliders - Blue */
    .stSlider > div > div > div {
        background-color: #2196F3;
    }

    /* Expander - Purple theme */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #F3E5F5 0%, #E1BEE7 100%);
        border-radius: 10px;
        font-weight: 700;
        color: #7B1FA2;
        border: 2px solid #CE93D8;
        padding: 12px;
    }

    /* Success/Info/Warning - Vibrant */
    .stSuccess {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border-left: 6px solid #4CAF50;
        border-radius: 10px;
    }
    .stInfo {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        border-left: 6px solid #2196F3;
        border-radius: 10px;
    }
    .stWarning {
        background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
        border-left: 6px solid #FF9800;
        border-radius: 10px;
    }
    .stError {
        background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);
        border-left: 6px solid #F44336;
        border-radius: 10px;
    }

    /* Divider - Rainbow gradient */
    hr {
        border: none;
        height: 4px;
        background: linear-gradient(90deg,
            #2196F3 0%,
            #00BCD4 16%,
            #4CAF50 33%,
            #8BC34A 50%,
            #FFC107 66%,
            #FF9800 83%,
            #F44336 100%);
        margin: 30px 0;
        border-radius: 2px;
    }

    /* Download buttons - Orange gradient */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #FF9800 0%, #F57C00 50%, #E65100 100%);
        color: white;
        border: none;
        border-radius: 14px;
        padding: 12px 28px;
        font-weight: 700;
        box-shadow: 0 6px 12px rgba(255, 152, 0, 0.4);
        transition: all 0.3s ease;
    }
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #F57C00 0%, #E65100 50%, #BF360C 100%);
        box-shadow: 0 8px 16px rgba(255, 152, 0, 0.5);
        transform: translateY(-3px);
    }

    /* Data frames - Blue border */
    [data-testid="stDataFrameResizable"] {
        border: 2px solid #2196F3;
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)


def generate_example_3x3():
    """Generate a pre-filled example with 3 jobs and 3 machines (for exact method)"""
    example = []
    # Define 3 jobs - same as Metod_exact.py for verification
    job_configs = [
        [(0,3), (1,2), (2,2)],  # J1: M1(3) -> M2(2) -> M3(2)
        [(1,2), (2,1), (0,1)],  # J2: M2(2) -> M3(1) -> M1(1)
        [(2,3), (0,1), (1,2)]   # J3: M3(3) -> M1(1) -> M2(2)
    ]

    for job_id, ops in enumerate(job_configs):
        ops_str = "\n".join([f"{m},{d}" for m, d in ops])
        example.append(ops_str)

    return example


def generate_example_5x5():
    """Generate a pre-filled example with 5 jobs and 5 machines"""
    example = []
    # Define 5 jobs with operations on different machines
    job_configs = [
        [(0,4), (1,3), (2,5), (3,2), (4,6)],
        [(1,5), (0,2), (3,4), (2,3), (4,2)],
        [(2,3), (3,6), (0,2), (1,4), (4,5)],
        [(3,2), (2,4), (1,3), (0,5), (4,3)],
        [(4,5), (3,3), (2,2), (1,4), (0,3)]
    ]

    for job_id, ops in enumerate(job_configs):
        ops_str = "\n".join([f"{m},{d}" for m, d in ops])
        example.append(ops_str)

    return example


def generate_example_10x10():
    """Generate a pre-filled example with 10 jobs and 10 machines"""
    example = []
    # Define 10 jobs with operations on different machines
    job_configs = [
        [(0,5), (1,3), (2,4), (3,6), (4,2), (5,3), (6,4), (7,5), (8,3), (9,2)],
        [(1,4), (0,2), (3,5), (2,3), (5,4), (4,2), (7,3), (6,4), (9,5), (8,2)],
        [(2,3), (3,4), (0,2), (1,5), (6,3), (5,2), (8,4), (7,3), (4,2), (9,3)],
        [(3,2), (2,5), (1,3), (0,4), (7,2), (6,3), (9,4), (8,2), (5,3), (4,2)],
        [(4,3), (5,2), (6,4), (7,3), (0,5), (1,2), (2,3), (3,4), (8,2), (9,3)],
        [(5,4), (4,3), (7,2), (6,5), (1,3), (0,2), (3,4), (2,3), (9,2), (8,4)],
        [(6,2), (7,3), (8,4), (9,2), (2,3), (3,4), (0,2), (1,3), (4,5), (5,2)],
        [(7,3), (6,2), (9,4), (8,3), (3,2), (2,3), (1,4), (0,2), (5,3), (4,2)],
        [(8,4), (9,2), (0,3), (1,4), (4,2), (5,3), (6,2), (7,4), (2,3), (3,2)],
        [(9,2), (8,3), (1,4), (0,2), (5,3), (4,2), (7,3), (6,4), (3,2), (2,3)]
    ]

    for job_id, ops in enumerate(job_configs):
        ops_str = "\n".join([f"{m},{d}" for m, d in ops])
        example.append(ops_str)

    return example


def main():
    # Title
    st.markdown("<h1 style='text-align: center;'>Job Shop Scheduler</h1>",
                unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Comparaison d'Algorithmes de Résolution</h3>",
                unsafe_allow_html=True)

    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")

        st.divider()

        # SA parameters
        st.subheader("Paramètres Recuit Simulé")

        temp_init = st.number_input(
            "Température initiale",
            min_value=100,
            max_value=5000,
            value=1000,
            step=100,
            help="Température de départ (défaut: 1000)"
        )

        cooling_rate = st.slider(
            "Taux de refroidissement",
            min_value=0.80,
            max_value=0.99,
            value=0.95,
            step=0.01,
            help="Facteur de refroidissement (défaut: 0.95)"
        )

        iter_per_temp = st.number_input(
            "Itérations/température",
            min_value=10,
            max_value=500,
            value=100,
            step=10,
            help="Nombre d'itérations par palier (défaut: 100)"
        )

        temp_min = st.number_input(
            "Température minimale",
            min_value=0.1,
            max_value=10.0,
            value=1.0,
            step=0.1,
            help="Température finale (défaut: 1.0)"
        )

    # Main content area
    st.markdown("---")

    # Input section - Manual entry only
    st.subheader("Définition du Problème JSP")

    col1, col2 = st.columns(2)
    with col1:
        n_jobs = st.number_input("Nombre de jobs", min_value=2, max_value=20, value=5)
    with col2:
        n_machines = st.number_input("Nombre de machines", min_value=2, max_value=20, value=5)

    st.info("Format: machine_id,durée (ex: 0,5 pour Machine 0, durée 5). Les machines sont numérotées de 0 à " + str(n_machines-1))

    # Info for CP-SAT
    if n_jobs > 15 or n_machines > 15:
        st.warning(f"Instance {n_jobs}x{n_machines} très grande. La méthode exacte (CP-SAT) peut prendre du temps. Le Recuit Simulé sera plus rapide.")
    else:
        st.info(f"Instance {n_jobs}x{n_machines} - Les deux méthodes sont disponibles. CP-SAT garantit l'optimal.")

    # Get example data - choose based on size
    if n_jobs <= 3 and n_machines <= 3:
        example_data = generate_example_3x3()
    elif n_jobs <= 5 and n_machines <= 5:
        example_data = generate_example_5x5()
    else:
        example_data = generate_example_10x10()

    # Ensure example_data matches current n_jobs
    if len(example_data) < n_jobs:
        # Extend with empty entries
        example_data.extend([""] * (n_jobs - len(example_data)))
    elif len(example_data) > n_jobs:
        # Trim
        example_data = example_data[:n_jobs]

    # Create input fields for each job
    jobs_input = []
    for j in range(n_jobs):
        col1, col2 = st.columns([1, 4])
        with col1:
            st.write(f"**Job {j}:**")
        with col2:
            ops_input = st.text_area(
                f"Opérations",
                value=example_data[j] if j < len(example_data) else "",
                key=f"job_{j}",
                height=150,
                help="Une opération par ligne: machine_id,durée",
                label_visibility="collapsed"
            )
            jobs_input.append(ops_input)

    st.markdown("---")

    # Parse problem
    problem = None
    jobs = []
    parse_error = False

    for j in range(n_jobs):
        operations = []
        for line in jobs_input[j].strip().split('\n'):
            if line.strip():
                try:
                    parts = line.strip().split(',')
                    machine_id = int(parts[0])
                    duration = int(parts[1])

                    # Validate machine_id
                    if machine_id < 0 or machine_id >= n_machines:
                        st.error(f"Job {j}: Machine ID {machine_id} invalide. Doit être entre 0 et {n_machines-1}")
                        parse_error = True
                        break

                    operations.append(Operation(machine_id, duration, j, len(operations)))
                except Exception as e:
                    st.error(f"Job {j}: Format invalide - {line}. Erreur: {e}")
                    parse_error = True
                    break

        if operations and not parse_error:
            jobs.append(Job(j, operations))

    if len(jobs) == n_jobs and all(len(job.operations) > 0 for job in jobs) and not parse_error:
        problem = JSPProblem(
            name=f"custom_{n_jobs}x{n_machines}",
            n_machines=n_machines,
            n_jobs=n_jobs,
            jobs=jobs
        )
        st.success(f"Problème créé: {n_jobs} jobs, {n_machines} machines")
    elif not parse_error:
        st.warning("Veuillez définir toutes les opérations pour tous les jobs")

    # Solve buttons
    if problem is not None:
        st.markdown("---")
        st.subheader("Résolution")

        col1, col2 = st.columns(2)

        with col1:
            exact_button = st.button("MÉTHODE EXACTE (CP-SAT)", use_container_width=True, type="primary")

        with col2:
            sa_button = st.button("RECUIT SIMULÉ", use_container_width=True, type="primary")

        st.info("La méthode exacte (CP-SAT) garantit l'optimal et est beaucoup plus rapide que l'énumération. Le recuit simulé est une heuristique rapide.")

        # Solve with CP-SAT Exact Method
        if exact_button:
            with st.spinner("Résolution exacte avec CP-SAT (Google OR-Tools)..."):
                try:
                    # Set time limit based on instance size
                    time_limit = 60 if (n_jobs <= 10 and n_machines <= 10) else 300
                    solver = CPSatSolver(time_limit_seconds=time_limit)
                    solution, stats = solver.solve(problem)

                    # Store in session state
                    st.session_state['exact_solution'] = solution
                    st.session_state['exact_stats'] = stats
                    st.session_state['problem'] = problem

                    status_msg = "OPTIMAL" if stats['optimal'] else "FAISABLE (timeout)"
                    st.success(f"Solution {status_msg} trouvée! Makespan: {stats['makespan']} (branches: {stats['branches']:,}, conflits: {stats['conflicts']:,})")
                except Exception as e:
                    st.error(f"Erreur lors de la résolution: {e}")

        # Solve with SA
        if sa_button:
            with st.spinner("Résolution avec Recuit Simulé..."):
                try:
                    solver = SimulatedAnnealingSolver(
                        temp_init=temp_init,
                        cooling_rate=cooling_rate,
                        iter_per_temp=iter_per_temp,
                        temp_min=temp_min,
                        verbose=False
                    )
                    solution, stats = solver.solve(problem)

                    # Store in session state
                    st.session_state['sa_solution'] = solution
                    st.session_state['sa_stats'] = stats
                    st.session_state['problem'] = problem
                    st.success(f"Optimisation terminée! Amélioration: {stats['improvement_percent']:.2f}%")
                except Exception as e:
                    st.error(f"Erreur lors de la résolution: {e}")

    # Display results stacked vertically
    if 'exact_solution' in st.session_state or 'sa_solution' in st.session_state:
        st.markdown("---")
        st.header("Résultats")

        # Exact method results (CP-SAT)
        if 'exact_solution' in st.session_state:
            st.subheader("Méthode Exacte (CP-SAT Google OR-Tools)")
            solution = st.session_state['exact_solution']
            stats = st.session_state['exact_stats']
            problem = st.session_state['problem']

            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                status_label = "OPTIMAL" if stats['optimal'] else "Makespan"
                st.metric(status_label, f"{stats['makespan']}")
            with col2:
                # Display CPU time in milliseconds if < 0.01s
                cpu_time = stats['cpu_time']
                if cpu_time < 0.01:
                    st.metric("Temps CPU", f"{cpu_time*1000:.2f} ms")
                else:
                    st.metric("Temps CPU", f"{cpu_time:.2f} s")
            with col3:
                st.metric("Branches", f"{stats['branches']:,}")
            with col4:
                st.metric("Statut", stats['status'])

            # Gantt chart
            title_suffix = "OPTIMAL" if stats['optimal'] else "Meilleure solution trouvée"
            gantt_fig = create_gantt_chart(solution, problem, title=f"Diagramme de Gantt - CP-SAT ({title_suffix})")
            st.plotly_chart(gantt_fig, use_container_width=True)

            # Machine utilization and download in columns
            col1, col2 = st.columns([2, 1])
            with col1:
                with st.expander("Détails CP-SAT"):
                    st.write(f"- **Algorithme**: Constraint Programming SAT")
                    st.write(f"- **Statut**: {stats['status']}")
                    st.write(f"- **Makespan**: {stats['makespan']}")
                    st.write(f"- **Branches explorées**: {stats['branches']:,}")
                    st.write(f"- **Conflits**: {stats['conflicts']:,}")
                    st.write(f"- **Temps CPU**: {stats['cpu_time']:.4f} s")
                    st.write(f"- **Wall time**: {stats['wall_time']:.4f} s")

                with st.expander("Utilisation des machines"):
                    util = solution.get_machine_utilization()
                    util_df = pd.DataFrame([
                        {"Machine": f"M{m}", "Utilisation": f"{u*100:.1f}%", "Taux": u}
                        for m, u in util.items()
                    ])
                    st.dataframe(
                        util_df.style.bar(subset=['Taux'], color='#4CAF50'),
                        use_container_width=True,
                        hide_index=True
                    )
            with col2:
                # Download solution
                solution_json = solution.to_dict()
                solution_json['problem'] = problem.to_dict()
                solution_json['statistics'] = stats

                st.download_button(
                    label="Télécharger solution (JSON)",
                    data=json.dumps(solution_json, indent=2),
                    file_name=f"solution_exact_{problem.name}.json",
                    mime="application/json",
                    use_container_width=True
                )

            st.markdown("---")

        # SA results
        if 'sa_solution' in st.session_state:
            st.subheader("Recuit Simulé")
            solution = st.session_state['sa_solution']
            stats = st.session_state['sa_stats']
            problem = st.session_state['problem']

            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Makespan", f"{stats['best_makespan']}")
            with col2:
                st.metric("Amélioration", f"{stats['improvement_percent']:.2f}%")
            with col3:
                # Display CPU time in milliseconds if < 0.01s
                cpu_time = stats['cpu_time']
                if cpu_time < 0.01:
                    st.metric("Temps CPU", f"{cpu_time*1000:.2f} ms")
                else:
                    st.metric("Temps CPU", f"{cpu_time:.2f} s")
            with col4:
                st.metric("Type", "Métaheuristique")

            # Gantt chart
            gantt_fig = create_gantt_chart(solution, problem, title="Diagramme de Gantt - Recuit Simulé")
            st.plotly_chart(gantt_fig, use_container_width=True)

            # Machine utilization and download in columns
            col1, col2 = st.columns([2, 1])
            with col1:
                with st.expander("Utilisation des machines"):
                    util = solution.get_machine_utilization()
                    util_df = pd.DataFrame([
                        {"Machine": f"M{m}", "Utilisation": f"{u*100:.1f}%", "Taux": u}
                        for m, u in util.items()
                    ])
                    st.dataframe(
                        util_df.style.bar(subset=['Taux'], color='#2196F3'),
                        use_container_width=True,
                        hide_index=True
                    )
            with col2:
                # Download solution
                solution_json = solution.to_dict()
                solution_json['problem'] = problem.to_dict()
                solution_json['statistics'] = stats

                st.download_button(
                    label="Télécharger solution (JSON)",
                    data=json.dumps(solution_json, indent=2),
                    file_name=f"solution_sa_{problem.name}.json",
                    mime="application/json",
                    use_container_width=True
                )

        # Comparison table
        if 'exact_solution' in st.session_state and 'sa_solution' in st.session_state:
            st.markdown("---")
            st.subheader("Comparaison des Algorithmes")

            exact_stats = st.session_state['exact_stats']
            sa_stats = st.session_state['sa_stats']

            # Format CPU time for display
            exact_cpu_display = f"{exact_stats['cpu_time']*1000:.2f} ms" if exact_stats['cpu_time'] < 0.01 else f"{exact_stats['cpu_time']:.2f} s"
            sa_cpu_display = f"{sa_stats['cpu_time']*1000:.2f} ms" if sa_stats['cpu_time'] < 0.01 else f"{sa_stats['cpu_time']:.2f} s"

            # Calculate gap
            gap = ((sa_stats['best_makespan'] - exact_stats['makespan']) / exact_stats['makespan']) * 100

            # Build comparison
            exact_label = f"CP-SAT ({exact_stats['status']})"
            exact_gap_text = '0.00% (optimal)' if exact_stats['optimal'] else 'Référence'

            comparison_df = pd.DataFrame({
                'Algorithme': [exact_label, 'Recuit Simulé'],
                'Makespan': [exact_stats['makespan'], sa_stats['best_makespan']],
                'Gap (%)': [exact_gap_text, f'{gap:.2f}%'],
                'Temps CPU': [exact_cpu_display, sa_cpu_display],
                'Type': ['CP-SAT (exact)', 'Heuristique']
            })

            # Highlight best
            def highlight_best(row):
                if row['Algorithme'].startswith('CP-SAT'):
                    return ['background-color: #C8E6C9'] * len(row)
                elif sa_stats['best_makespan'] == exact_stats['makespan']:
                    return ['background-color: #C8E6C9'] * len(row)
                return [''] * len(row)

            st.dataframe(comparison_df.style.apply(highlight_best, axis=1), use_container_width=True, hide_index=True)

            # Determine winner
            if not exact_stats['optimal']:
                st.info(f"CP-SAT n'a pas prouvé l'optimalité (timeout). Makespan trouvé: {exact_stats['makespan']}")

            if sa_stats['best_makespan'] == exact_stats['makespan']:
                st.success(f"Excellent! Le Recuit Simulé a trouvé la même solution que CP-SAT: {sa_stats['best_makespan']} (0% gap)")
            elif gap <= 5:
                st.info(f"Très bon résultat! Le Recuit Simulé est à {gap:.2f}% de CP-SAT ({sa_stats['best_makespan']} vs {exact_stats['makespan']})")
            else:
                st.warning(f"Le Recuit Simulé est à {gap:.2f}% de CP-SAT ({sa_stats['best_makespan']} vs {exact_stats['makespan']}). Essayez d'augmenter les paramètres.")


if __name__ == "__main__":
    main()
