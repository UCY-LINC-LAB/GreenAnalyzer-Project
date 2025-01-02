![GreenAnalyzer Icon](https://ucy-linc-lab.github.io/GreenAnalyzerProject//images/logopic/logo_greenanalyzer.png)
# *A framework for Geo-distRibuted Edge-cloud Energy consumption ANALYsis towards Zero Emission Rates*

Geo-distributed data centers operate continuously, requiring substantial electrical energy and contributing to global carbon emissions. In 2022, the electricity consumption of data centers was estimated to be between 240-340 TWh, accounting for approximately 1-1.3% of global electricity demand. This consumption leads to significant operational costs and environmental impact, with around 330 million metric tons of CO2 emissions in 2020. Driven by the dual pressures of operational expenses and climate change, both large and small data center operators are increasingly focusing on providing carbon-neutral services. This shift is further motivated by initiatives such as the European Green Deal and the UK net-zero strategy.

**GreenAnalyzer** is a framework provided by the University of Cyprus's Laboratory for Internet Computing (LInC) to address the pressing challenges of energy consumption and carbon emissions in geo-distributed edge data centers (DCs). Recognizing the significant energy demands and environmental impact of data centers, GreenAnalyzer aims to enhance the sustainability of these operations through advanced modeling and predictive analytics. By integrating various web APIs with state-of-the-art machine learning (ML) and artificial intelligence (AI) techniques, GreenAnalyzer focuses on providing detailed insights into the energy needs of edge compute nodes and the forecast energy output from renewable energy sources (RES) like photovoltaic (PV) systems. These predictive capabilities enable data center operators to optimize their energy use, minimize carbon emissions, and reduce operational costs, addressing the need for improved energy efficiency.

Core Functionalities:

* **Energy Consumption Modeling:** GreenAnalyzer utilizes pre-trained models to predict the energy consumption of various components within a data center, including individual processes, servers, and racks. These models are based on detailed workload utilization characteristics, allowing for accurate predictions and efficient energy management.

* **Energy Production Forecasting:** The framework employs a hybrid science-guided AI approach, combining traditional scientific models with advanced ML techniques to forecast energy production from renewable sources, particularly PV systems. This method ensures accurate and reliable predictions by accounting for various influencing factors such as weather conditions and temporal variations.

* **Integration with External APIs:** GreenAnalyzer enriches its predictive models with real-time data from publicly available APIs, including weather conditions, energy costs, and carbon emissions. This integration ensures that the framework can provide comprehensive and up-to-date insights into the energy dynamics of data centers.

* **RESTful API:** To facilitate seamless integration with other systems, GreenAnalyzer offers a RESTful API that allows external applications, such as cloud schedulers and dashboards, to access its predictions and analyses. This API enables data center operators to make informed decisions based on accurate and timely data.

* **Open Source:** GreenAnalyzer is developed as an open-source project, with its codebase, models, and datasets made publicly available. This commitment to open-source principles promotes transparency, collaboration, and further research in sustainable data center operations.

GreenAnalyzer represents a significant step forward in the quest for sustainable data center operations, offering a comprehensive, data-driven approach to energy management that benefits both the environment and the economy.

*Keywords: Energy Modeling, Green Data Centers, Machine Learning, Renewable Energy, Carbon Emissions, Edge Computing*

### Publications

For more details about Fogify and our scientific contributions, you can read the papers of [GreenAnalyzer](http://linc.ucy.ac.cy/index.php?id=12).
If you would like to use GreenAnalyzer for your research, you should include at least on of the following BibTeX entries. 

GreenAnalyzer's energy modeling paper BibTeX citation:
```
@INPROCEEDINGS{Kasioulis2024,
  author={Michalis Kasioulis, Moysis Symeonides, Giorgos Ioannou, George Pallis, Marios D. Dikaiakos},
  booktitle={Proceedings of the 12th IEEE International Conference on Cloud Engineering},
  series={IC2E `24},
  title={Energy modeling of inference workloads with AI accelerators at the Edge: A benchmarking study},
  year={2024},
  type={conference}
  }
```

GreenAnalyzer's renewable sources and carbon emission modeling paper BibTeX citation:
```
@INPROCEEDINGS{Symeonides2024,
  author={Moysis Symeonides, Nicoletta Tsiopani, Georgios Maouris, Demetris Trihinas, George Pallis, Marios D. Dikaiakos},
  booktitle={Proceedings of the 17th IEEE/ACM International Conference on Utility and Cloud Computing},
  series={UCC `24},
  title={CarbonOracle: Automating Energy Mix & Renewable Energy Source Forecast Modeling for Carbon-Aware Micro Data Centers},
  year={2024},
  type={conference}
  }
```

### Acknowledgements
GreenAnalyzer has indirectly received funding from the European Union’s Horizon Europe research and innovation action programme, via the [aerOS](https://aeros-project.eu/) Open Call issued and executed under the aerOS project (Grant Agreement no. 101069732).

### License
The framework is open-sourced under the Apache 2.0 License base. The codebase of the framework is maintained by the authors for academic research and is therefore provided "as is".
