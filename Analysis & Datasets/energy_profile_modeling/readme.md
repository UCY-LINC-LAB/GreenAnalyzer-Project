# **Energy Datasets & Modeling**

This directory contains essential resources related to energy consumption datasets and power modeling, primarily developed for the **aerOS** and **GreenAnalyzer** projects. These resources aim to facilitate energy-efficient operations and contribute to advancing sustainable computing solutions.

## **Energy Datasets**

We collected energy consumption datasets by running a custom stressor on four distinct node types. Each dataset captures critical performance and power metrics under various workloads. Below is a detailed description of the datasets:

- **`rpi4.csv`:**  Contains data from our stressor executed on a **Raspberry Pi 4**, a low-power ARM-based device commonly used for edge applications.  

- **`nc3.csv`:**  Represents data collected from a **server equipped with an Intel® Xeon® CPU X5690 @ 3.47GHz**, featuring 12 cores and 12GB of memory. This server demonstrates a balance between computational capability and resource constraints.  

- **`nc11.csv`:**  Includes results from a **high-performance server powered by an Intel® Xeon® CPU X5650 @ 2.67GHz**, offering 24 cores and 70GB of memory. This setup was selected for experiments requiring extensive computational power.  

- **`aeros-server.csv` & `aeros-server-2.csv`:**  These datasets were extracted from tests conducted on pods deployed on the **aerOS platform in Pilot 2 (Poland)**. These experiments aim to assess the aerOS platform's energy efficiency.

## **Power Modeling**

The file **`modeling_of_CPU.ipynb`** contains the implementation of our CPU power modeling methodology. This Jupyter Notebook includes:  
- Data preprocessing steps for the collected datasets.  
- Detailed energy modeling techniques used for the aerOS project.  
- Scripts to replicate the experimental setup and validate results.  

The modeling experiments provide insights into the energy behavior of different systems, offering valuable information for optimizing energy consumption in heterogeneous environments.