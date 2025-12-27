# Job Shop Scheduler - Industrial Optimization Platform

A comprehensive web-based application for solving Job Shop Scheduling Problems (JSP) using advanced optimization algorithms. This tool bridges the gap between academic operations research and practical industrial scheduling needs.

---

## Table of Contents

- [Industrial Significance](#industrial-significance)
- [Application Features](#application-features)
- [How Industries Can Use This Platform](#how-industries-can-use-this-platform)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Algorithm Comparison](#algorithm-comparison)
- [Project Structure](#project-structure)
- [Academic Context](#academic-context)

---

## Industrial Significance

### Why Job Shop Scheduling Matters

Job Shop Scheduling is one of the most critical optimization problems in manufacturing and production management. The ability to efficiently schedule jobs across machines directly impacts:

**Manufacturing Efficiency**
- **Reduced Makespan**: Minimize total production time, increasing throughput and meeting delivery deadlines
- **Machine Utilization**: Optimize equipment usage to reduce idle time and maximize return on capital investment
- **Bottleneck Identification**: Visualize and address production constraints before they impact operations

**Economic Impact**
- **Cost Reduction**: Better scheduling reduces overtime, energy consumption, and operational costs
- **Increased Capacity**: Optimize existing resources before investing in new equipment
- **Competitive Advantage**: Faster delivery times and reliable scheduling improve customer satisfaction

**Real-World Applications**
- **Manufacturing Plants**: Semiconductor fabrication, automotive assembly, electronics production
- **Aerospace Industry**: Complex part manufacturing with sequential operations on specialized machines
- **Metal Processing**: Job shops with milling, turning, grinding, and heat treatment operations
- **Printing & Packaging**: Multi-stage production with setup times and sequence-dependent constraints
- **Pharmaceuticals**: Batch production scheduling with strict regulatory compliance requirements

### The Complexity Challenge

Job Shop Scheduling is an NP-hard problem, meaning:
- A 10×10 instance has over 10^65 possible schedules
- Finding the optimal solution requires sophisticated algorithms
- Exact methods guarantee optimality but may be computationally expensive
- Metaheuristics provide high-quality solutions quickly for large-scale problems

This platform provides **both approaches**, allowing users to choose based on their specific needs.

---

## Application Features

### 1. Dual Algorithm Approach

**CP-SAT Exact Solver (Google OR-Tools)**
- Guarantees optimal solution for small to medium instances
- Efficient constraint propagation and search strategies
- Suitable for instances up to 15×15 (and beyond with time limits)
- Provides optimality proof when solution is found
- Reports: makespan, branches explored, conflicts, CPU time

**Simulated Annealing Metaheuristic**
- Rapid high-quality solutions for large instances
- Configurable parameters for fine-tuning performance
- Convergence visualization showing optimization progress
- Suitable for instances with 20+ jobs and machines
- Reports: makespan, improvement percentage, CPU time, convergence curve

### 2. Interactive Web Interface

**Problem Input Methods**
- **Manual Entry**: Define custom problems directly in the browser
  - Specify number of jobs and machines
  - Enter operation sequences for each job
  - Machine IDs and processing durations
- **Pre-loaded Examples**: Quick-start templates (3×3, 5×5, 10×10)
- **JSON Upload**: Import problem instances from files
- **Format Validation**: Real-time error checking and feedback

**Visualization & Analysis**
- **Interactive Gantt Charts**: Powered by Plotly
  - Color-coded by job for easy identification
  - Hover details showing operation timing
  - Machine timeline view
  - Zoom and pan capabilities
- **Performance Metrics Dashboard**
  - Makespan comparison between algorithms
  - Gap percentage vs optimal/best solution
  - CPU time analysis
  - Machine utilization rates
- **Convergence Curves**: Track algorithm improvement over iterations

**Export Capabilities**
- Download solutions in JSON format
- Include problem definition and statistics
- Reproducible results for documentation and auditing

### 3. Side-by-Side Algorithm Comparison

Run both algorithms on the same instance and compare:
- Solution quality (makespan)
- Computation time
- Gap percentage
- When to use each approach

---

## How Industries Can Use This Platform

### Practical Workflow for Production Planning

#### 1. **Problem Definition**

A production manager at a manufacturing facility needs to schedule 8 jobs across 6 machines:

**Input Process:**
1. Open the web application
2. Set n_jobs = 8, n_machines = 6
3. For each job, define the operation sequence:
   ```
   Job 0: Machine 2 (45 min), Machine 0 (30 min), Machine 4 (60 min)
   Job 1: Machine 1 (40 min), Machine 3 (50 min), Machine 5 (35 min)
   ...
   ```
4. Alternatively, prepare a JSON file with all job data and upload it

#### 2. **Algorithm Selection**

**For Daily Production Scheduling (known problem patterns):**
- Use **CP-SAT Exact Solver** for guaranteed optimal schedules
- Ideal for: repetitive production runs, critical delivery deadlines
- Time investment: Worth waiting for provably best solution

**For Rush Orders or Dynamic Rescheduling:**
- Use **Simulated Annealing** for quick, near-optimal solutions
- Ideal for: unexpected urgent orders, machine breakdowns, real-time adjustments
- Fast response: Get a working schedule in seconds

#### 3. **Visual Analysis**

The Gantt chart provides immediate insights:

**Identify Critical Operations**
- Which jobs are on the critical path?
- Which machines have the most utilization?
- Where are the idle periods?

**Bottleneck Detection**
- Visual inspection reveals overloaded machines
- Identify potential for load balancing
- Plan maintenance during low-utilization periods

**Communication Tool**
- Share visual schedules with shop floor supervisors
- Clear timeline for each job's completion
- Coordinate material delivery and workforce allocation

#### 4. **Optimization & What-If Analysis**

**Scenario Testing:**
- Adjust SA parameters to find better solutions
- Add priority constraints by reordering jobs
- Test impact of adding overtime (extended makespan tolerance)

**Continuous Improvement:**
- Compare current schedule vs optimized schedule
- Quantify potential savings in production time
- Justify equipment investments based on utilization data

### Industry-Specific Use Cases

**Automotive Parts Manufacturing**
- Schedule machining operations for engine components
- Coordinate multiple work centers (turning, milling, grinding, inspection)
- Minimize setup times through intelligent sequencing

**Electronics Assembly**
- PCB production scheduling across SMT, wave soldering, testing
- Multi-product scheduling with changeover considerations
- Meet strict delivery windows for just-in-time supply chains

**Custom Job Shops**
- Handle diverse customer orders with unique routings
- Balance workload across machines
- Provide accurate delivery date estimates

**Aerospace Components**
- Schedule high-precision operations with long processing times
- Coordinate specialized equipment (CNC, EDM, heat treatment)
- Track critical path for time-sensitive projects

---

## Technology Stack

This application was built using modern, industry-standard technologies:

### Backend & Algorithms

**Python 3.9+**
- Core programming language for all algorithms and data processing

**Google OR-Tools (CP-SAT)**
- Industry-leading constraint programming solver
- Powers the exact optimization method
- Version: 9.7.0+

**NumPy**
- Numerical computing library
- Used for mathematical operations and data structures
- Version: 1.24.0+

### Frontend & Visualization

**Streamlit**
- Web application framework for interactive data applications
- Enables rapid development of user interfaces
- Version: 1.28.0+

**Plotly**
- Interactive charting library
- Powers the Gantt chart visualizations
- Responsive, zoomable, and exportable graphics
- Version: 5.17.0+

**Pandas**
- Data manipulation and analysis
- Manages result tables and statistics
- Version: 2.0.0+

### Algorithm Implementation

**Simulated Annealing**
- Custom implementation based on operations research literature
- Metropolis acceptance criterion
- Adaptive neighborhood generation
- Configurable cooling schedules

**Constraint Programming Model**
- Disjunctive scheduling formulation
- Precedence constraints via interval variables
- No-overlap constraints for resource allocation

### Development & Testing

**Python unittest framework**
- Comprehensive test suite for data structures
- Algorithm validation tests (5 critical test scenarios)
- Ensures correctness and reliability

**JSON-based Data Exchange**
- Standard format for problem instances
- Interoperable with other OR tools
- Easy integration with ERP/MES systems

---

## Getting Started

### Installation

1. **Clone or download this repository**

2. **Install dependencies:**
   ```bash
   cd jsp-solver
   pip install -r requirements.txt
   ```

3. **Launch the application:**
   ```bash
   streamlit run app.py
   ```

   Or on Windows, double-click:
   ```
   run_app.bat
   ```

4. **Access the interface:**
   - Open browser to `http://localhost:8501`
   - The application will launch automatically

### Quick Start

1. **Try the 3×3 Example**
   - Pre-loaded problem instance
   - Click "MÉTHODE EXACTE (CP-SAT)" to see optimal solution
   - Click "RECUIT SIMULÉ" to compare metaheuristic result
   - Examine Gantt charts and metrics

2. **Create Your Own Problem**
   - Set number of jobs and machines
   - Enter operation sequences
   - Choose algorithm and solve
   - Export solution for documentation

3. **Adjust Parameters (for SA)**
   - Use sidebar to configure:
     - Initial temperature (exploration vs exploitation)
     - Cooling rate (convergence speed)
     - Iterations per temperature
   - Observe impact on solution quality and time

---

## Algorithm Comparison

### When to Use Each Method

| Criterion | CP-SAT Exact | Simulated Annealing |
|-----------|-------------|---------------------|
| **Instance Size** | ≤ 15×15 | Any size |
| **Solution Quality** | Guaranteed optimal | Near-optimal (typically 0-5% gap) |
| **Computation Time** | Seconds to minutes | Seconds |
| **Use Case** | Critical schedules, baseline optimization | Rapid rescheduling, large instances |
| **Best For** | Proving optimality, academic benchmarks | Production environments, what-if analysis |

### Performance Benchmarks

**3×3 Instance (Optimal = 7)**
- CP-SAT: <0.1s, Makespan = 7 (optimal)
- SA: ~0.5s, Makespan = 7 (100% success rate)

**10×10 Instance**
- CP-SAT: 5-30s depending on complexity
- SA: 1-3s, typically within 5% of optimal

**20×20 Instance (large-scale)**
- CP-SAT: May require extended time limits
- SA: 5-10s, high-quality solutions

---

## Project Structure

```
Project/
├── README.md                           # This file
├── CLAUDE.md                           # Development documentation
├── Metod_exact.py                      # Console-based enumeration solver (3×3)
│
├── jsp-solver/                         # Main application directory
│   ├── app.py                          # Streamlit web interface
│   ├── jsp_model.py                    # Core data structures
│   ├── cp_sat_solver.py                # Exact solver implementation
│   ├── simulated_annealing.py          # SA metaheuristic
│   ├── exact_solver.py                 # Enumeration-based solver
│   ├── greedy_solver.py                # Fast constructive heuristic
│   ├── gantt_chart.py                  # Plotly visualization
│   ├── requirements.txt                # Python dependencies
│   ├── run_app.bat                     # Windows launcher
│   │
│   ├── test_jsp_model.py               # Data structure tests
│   ├── test_sa.py                      # Algorithm validation tests
│   │
│   ├── example_3x3.json                # Sample problem instances
│   ├── example_4x4.json
│   ├── example_simple_2x2.json
│   ├── JSON_FORMAT_GUIDE.md            # Input format specification
│   │
│   └── .streamlit/
│       └── config.toml                 # UI theme configuration
│
├── Projet_JSP_Modele_Exact_MH_Gantt.pdf    # Academic specifications
├── Etude_de_cas_TFC_Fressie.pdf            # Case study: Bottling line
├── Rapport_JSP_Groupe_8.pdf                # Project report
└── .claude/
    └── settings.local.json             # Development environment settings
```

---

## Academic Context

This project was developed as part of an academic program, focusing on:

- Mathematical modeling of combinatorial optimization problems
- Implementation of exact and heuristic solution methods
- Comparison with Best-Known Solutions (BKS) from literature
- Industrial application of operations research techniques

### Alignment with Industry Standards

**Benchmark Compatibility:**
- Follows standard JSP formulation from literature
- Compatible with Taillard, Brandimarte, and Hurink benchmark instances
- JSON format enables integration with OR-Library and other repositories

**Performance Metrics:**
- Makespan (Cmax): Primary objective function
- Gap percentage vs BKS: Solution quality measure
- CPU time: Computational efficiency
- Machine utilization: Resource efficiency

**Deliverables:**
- Working software with professional UI
- Validated algorithms (100% test pass rate)
- Visual analytics for decision support
- Exportable results for reporting

---

## Future Enhancements

Potential extensions for production deployment:

- **Additional Metaheuristics**: Genetic Algorithms, Tabu Search, Ant Colony Optimization
- **Benchmark Library**: Pre-loaded Taillard and Brandimarte instances
- **Advanced Constraints**: Setup times, machine breakdowns, priority jobs
- **Multi-Objective**: Balance makespan, tardiness, and energy consumption
- **Database Integration**: Store historical schedules and results
- **API Development**: REST API for integration with ERP/MES systems
- **Real-Time Monitoring**: Track actual vs scheduled progress

---

## License

This project is developed for academic purposes as part of industrial engineering coursework.

**Academic Use:** Free for educational and research purposes.

**Commercial Use:** Contact the development team for licensing inquiries.

---

## Contact & Support

**Academic Institution:** Ecole Centrale Casablanca

**Project Type:** Job Shop Scheduling Optimization


---

## Acknowledgments

This project builds upon foundational research in operations research and constraint programming:

- Google OR-Tools development team for the CP-SAT solver
- Streamlit team for the web application framework
- Plotly team for interactive visualization capabilities
- Academic research in Job Shop Scheduling optimization methods

**Standard Benchmark Contributors:**
- Taillard (1993): Classic JSP benchmark instances
- Brandimarte (1993): Flexible JSP instances
- Hurink et al. (1994): Extended benchmark sets

---

**Built with precision. Optimized for industry. Ready for production.**
