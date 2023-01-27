# ICER, Integral Circular Economy Report of the Netherlands


## Intro

"The ICER report presents the state of affairs of the transition towards a circular economy in the Netherlands and contains guidelines for government policy on such a transition. The report describes the actions of stakeholders in society, the resources they are deploying and the government's intervention measures. It provides a summary of the Dutch use of raw materials and the associated environmental pressure and socio-economic effects. An ICER report will be published once every two years." The publishing body of the ICER is the Netherlands Environmental Assessment Agency or 'Planbureau voor de Leefomgeving' or 'PBL' in Dutch.

- PBL, 2023

The final version of the 2023 ICER can be found here:

https://www.pbl.nl/nieuws/2023/icer-2023-circulaire-doelen-liggen-nog-ver-buiten-bereik

For the 2023 edition of the ICER several new topics were explored, commissioned by the Inter Provincial Counsel 'Interprovinciaal Overleg' or 'IPO' in Dutch. Since the final version of ICER 2023 included a summarized text based on the research results, this repository allows access to all underlying research methods and (desensitized) data sources. The innovation that took place centered around the integration of various public data sources on national and sub-national levels. We share the knowledge and tools of using public data to inform decision-making for a sustainable world. The goal is to normalize this practice for projects that use public resources, such as funding and data. 

The research focused on the developments of four indicators to be calculated per Dutch province:

1) The Domestic Material Input and Domestic Material Consumption. In other words, the total input and consumption of material resources per province. 

2) The waste management improvement potential. The possibility for higher-value/more sustainable waste management for the waste flows originating in the province. 

3) The environmental impact -expressed as environmental costs- of the total material input (based on indicator 1) per province. 

4) The supply risk of the (critical) abiotic raw materials in the total material input per province. 


## Why this research?

The importance of calculating these indicators on the provincial level is to assist sub-national decision-makers in achieving the goals set out in national policy documents. The lack of context-specific data makes it difficult for sub-national governments to understand their position within the generalized picture of the Netherlands, and their action perspectives. Provinces are the right intermediary layer between the national and municipal governments. In other words, close enough to the top to discuss and execute the top-down vision, but close enough to the local context to make it work in practice with local stakeholders. 
By providing them with the initial estimates of their material consumption, waste management improvement potential, environmental impact, and resource supply risks, the first steps towards identifying opportunities and requirements for action can be taken. 

By partaking in data-driven research and innovation we discovered and unlocked essential digital public assets to (local) governments, suggested improvements for data collection and storage based on the newly identified needs, and assisted them with in-house knowledge development and data-driven decision-making. 


## Why these indicators?

1) Domestic Abiotic Material Input and Consumption
The Dutch government has set the goal to reduce their consumption of primary abiotic resources by 50% in 2030. Despite this goal being set in 2016, the current level of consumption has never been quantified on a national level, let alone a sub-national level. To understand where and how to take action, we must first know the quantity and type of resource consumption among the provincies in the country. 

This research contains the first attempt at calculating the consumption level of abiotic resource consumption (the distinction between primary and secondary abiotic resources is not yet possible given the data) on a provincial basis, and has set in motion ongoing intra-governmental research and data sharing collaborations. 

2) Waste Processing Improvement Potential
Waste contains valuable resources that are lost if suboptimal waste processing methgods are applied. Based on company-specific public data alternative higher-value/more sustainable processing methods were identified in the Netherlands based on the R-ladder/Ladder van Lansink principles. 

We identified best-practices in the Netherlands for all company-based reported waste streams. This analysis revealed that according to these data the majority of all waste is proessed suboptimally. By identifying province-based best-practices, provncial governments are able to exchange succesful and sustainable practices, and develop requirements for high-value/sustainable processing within their jurisdiction.

3) Environmental Impact of Material Input
Material input into a province comes at an environmental cost. The distribution and quantity of the impact across the imported goods and policy frameworks for value chains (known as Transition Agendas), aides regional decision-makers in the process of identifying the areas for improvement, and relating this to local industries and activities.

As a result of the environmental impact calculation of goods, calculated on the provincial inputs (DMI), regional trends of (industrial) activities were presented. These differences between provinces highlighted the importance of regional data-based decision-making as Dutch national averages failed to provide the nuanced characteristics of each individual provinces and their regional challenges. 

4) Supply risk of (critical) abiotic resources
Developments in the fields of high-tech industry, geo-politics, and energy, have resulted in a strong dependency by the Netherlands on foreign imported (critical) abiotic resources. Knowing which imported goods contain these materials, and which ones of those are at risk for supply-chain disruptions and price fluctuations, helps identify the local economic sectors and industries at most risk, and facilitates strategic decision-making. The analysis reviewed 64 abiotic resources, of which 25 deemed critical by the European Commission (https://rmis.jrc.ec.europa.eu/?page=crm-list-2020-e294f6).

The results provided regional decision-makers with estimates on the (critial) abiotic resources in their imported goods, their value, supply risks and potential for price fluctuations. This information creates awareness, and highlights new opportunities for the development of (regional) strategic value-chain creation.


## Data sources

This research made use of three main data sources:

1) Mandatory company waste registrations to the National Waste Registry ('Landelijk Meldpunt Afvlastoffen' or 'LMA' in Dutch). 

Due to the individual traceability of waste streams to companies, this dataset can only be published publicly in an aggregated way. However, civil servants in the Netherlands can request data from the organisation directly. 

2) Statistics on the transportation of goods by the Dutch Central Bureau of Statistics (CBS).

Due to the continual development of this dataset it will not be published here. Rather, the most recent version can be requested by emailing c.deblois@cbs.nl.

3) The distribution of (critical) abiotic resources per product by the Netherlands Organisation for Applied Scientific Research ('Nederlandse Organisatie voor Toegepast Natuurwetenschappelijk Onderzoek' or 'TNO' in Dutch).

## How to run the analysis

If you have already received access to the full data package:

1) Clone or fork the project

2) Optional: Create and activate a python-environment for Python 3.7

3) Install dependencies with

pip install -r requirements-dev.txt

4) Run each code for the 4 indicators

If you need access to the full data package, please contact the following people to receive the permissions including your motivation:
1) Chris de Blois ( c.deblois@cbs.nl ) from CBS for regional material input, output and throughput table per province;
2) Henk Verwoerd ( henk.verwoerd@rws.nl ) from LMA for amounts of waste production in tonnes per province per EWC code in 2020;

Once you have permission from both of them to receive access to the underlying data, please send an email to info@monitorce.nl with proof of permissions and you will receive the data packages from us.

## Data file structure

| Path                                                | Description                                                                                                                                             | Access    | Used for ind. |
|-----------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|---------------|
| data/CBS/Regionale_stromen_2015-2020_provincie.xlsx | Regional material input, output and throughput, source: CBS                                                                                             | On demand | 1, 3, 4       |
| data/LMA/All_treatments_per_code_per_province.xlsx  | Amounts of waste production in tonnes per province per EWC code, 2020, source: LMA & geoFluxus                                                          | On demand | 2             |
| data/TNO/CRM_per_kg_CE25.csv                        | Amounts of abiotic raw materials, g per kg of each product group, source: TNO & geoFluxus                                                               | Open      | 4             |
| data/TNO/Supply_security_indicators.csv             | Price, volatility and HHI of abiotic raw materials, source: TNO                                                                                         | Open      | 4             |
| data/geoFluxus/alternatives_exclude_processes.csv   | Combinations of EWC codes and processing methods that cannot be realistic (the list is not exhaustive and based on real occurrences), source: geoFluxus | Open      | 2             |
| data/geoFluxus/cbs_biotisch_abiotisch.csv           | Assignment of CBS product groups according to their predominant origin, source: geoFluxus                                                               | Open      | 1             |
| data/geoFluxus/mki_per_TA_per_provincie.csv         | Environmental cost of material input per transition agenda per province in EUR, 2020, source: geoFluxus                                                 | Open      | 3             |
| data/geoFluxus/R-ladder.xlsx                        | Assignment of LMA processing methods to waste treatment hierrachy (based on R-ladder), including restrictions, source: geoFluxus                        | Open      | 2             |
| data/geoFluxus/Ind.3_model_v1.1.xlsx                | The excel model used to produce mki_per_TA_per_provincie.csv, source: geoFluxus                                                                         | On demand | 3             |
| data/geoFluxus/Ind.4_model_v1.8.xlsx                | The excel model used to produce CRM_per_kg_CE25.csv, source: geoFluxus & TNO                                                                            | On demand | 4             |
| data/EWC_NAMES.xlsx                                 | List of European Waste Classification codes and their names (NL), source: Eurostat                                                                      | Open      | 2             |
| data/PROCESS_NAMES.xlsx                             | List of LMA codes and their names (NL), source: LMA                                                                                                     | Open      | 2             |
