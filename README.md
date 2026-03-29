# TNCAM-Robotic_Welding_Simulator

![Project Banner](https://img.shields.io/badge/Robotics-Welding-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![CoppeliaSim](https://img.shields.io/badge/CoppeliaSim-Edu-orange)

**TNCAM (The New Computer-Aided Manufacturing)** is a professional-grade robotic welding simulation environment built on top of **CoppeliaSim** (formerly V-REP). It provides a comprehensive suite for path designing, motion control, and safety monitoring of industrial welding robots.

## 🚀 Features

- **Interactive GUI**: A user-friendly Tkinter-based control panel.
- **Precision Path Designer**: Create and edit weld paths in real-time.
- **Advanced Kinematics**: Integrated Inverse Kinematics (IK) solver for smooth 6-DOF robot motion.
- **Safety Controller**: Real-time collision detection and obstacle avoidance.
- **Data Logging**: Comprehensive logging of joint states, tool positions, and welding KPIs.
- **CoppeliaSim Integration**: Seamless remote API communication for physics-based simulation.

## 🛠️ Prerequisites

- **CoppeliaSim**: Recommended version 4.1+ (Edu or Player).
- **Python 3.8+**: With `numpy`, `opencv-python`, and `tkinter`.

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sakrish205/TNCAM-Robotic_Welding_Simulator.git
   cd TNCAM-Robotic_Welding_Simulator
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **CoppeliaSim Setup**:
   - Open your welding scene in CoppeliaSim.
   - Ensure the Remote API server is running on port **19997**.

## 🚦 Usage

1. **Launch the Simulation**:
   ```bash
   python run_simulation.py
   ```

2. **Connect**: Click the **Connect** button in the GUI to establish communication with CoppeliaSim.
3. **Load Path**: Use the **Load CSV** or **Path Designer** to define the welding trajectory.
4. **Execute**: Click **Execute Path** to begin the welding process.

## 📂 Project Structure

- `run_simulation.py`: Main entry point and GUI.
- `requirements.txt`: Project dependencies.
- `.gitignore`: Git exclusion rules.
- `LICENSE`: MIT License file.
- `src/`: Core logic modules (IK, Control, Safety, Logging).
- `data/`: Input paths and output logs.
- `assets/`: 3D models and meshes.

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---
*Developed by the TNCAM Team.*
