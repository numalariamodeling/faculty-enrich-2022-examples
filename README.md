# Malaria Modeling Faculty Enrichment Program 2022
## Technical track (EMOD)

Example scripts for the [weekly lessons](https://faculty-enrich-2022.netlify.app/lessons/) of the faculty enrichment program 2022.



### Week 1: Overview of EMOD

[Lesson Week 1](https://faculty-enrich-2022.netlify.app/lessons/week-1/)


#### Instructions:

- Save copy of `simtools.ini` to Week-1 directory and adjust paths `<USERNAME>` with your username  
- Navigate to `Week-1` via `cd` to make this working directory
- Run simulation via `python run_example_sim.py`
- Wait simulation to finish (~20 minutes)
- Update expt_id in `analyze_example_sim.py`
- Run analyzer via `python analyze_example_sim.py`
- Inspect `simulation_outputs` to see generated simulation results
- Done!


<details><summary><span>Terminal output after successful submission of experiment</span></summary>
<p>

![img](../static/w1.1_console_runsim.png)
</p>
</details>


<details><summary><span>Terminal output after successful submission of analyzer</span></summary>
<p>

![img](../static/w1.1._console_analyzer.png)
</p>
</details>




### Week 2: Basic building blocks of EMOD

[Lesson Week 2](https://faculty-enrich-2022.netlify.app/lessons/week-2/)

EMOD How To's:

- [Create a demographics file](https://faculty-enrich-2022.netlify.app/modules/emod-how-to/emod-how-to/#create-a-demographics-file)
- Create a climate file 
- [Update config parameters](https://faculty-enrich-2022.netlify.app/modules/emod-how-to/emod-how-to/#update-config-parameters)


#### Instructions:

- Save copy of `simtools.ini` to Week-2 directory and adjust paths `<USERNAME>` with your username
- Copy the `run_example_sim.py` and `analyze_example_sim.py` from Week-1 to this folder (Week-2)
- Create _demographics_ and _climate_ files via `generate_input_files.py`
- Update default parameters in `python run_example_sim.py`:
    - _Demographics_Filenames_: 
      ```
      cb.update_params({'Demographics_Filenames': ['my_demographics.json'],
              'Age_Initialization_Distribution_Type': 'DISTRIBUTION_COMPLEX'})
      ```
    - _Climate_Model_ and Filenames: 
      ```
        cb.update_params({
            "Vector_Species_Names": [],
            'x_temporary_Larval_Habitat': 0,
            'Air_Temperature_Filename': 'Ghana_30arcsec_air_temperature_daily.bin',
            'Land_Temperature_Filename':  'Ghana_30arcsec_air_temperature_daily.bin',
            'Rainfall_Filename':  'Ghana_30arcsec_rainfall_daily.bin',
            'Relative_Humidity_Filename': 'Ghana_30arcsec_relative_humidity_daily.bin',
            'Climate_Model': 'CLIMATE_BY_DATA'
        })
      ```
- Run simulation via `python run_example_sim.py`
- Wait simulation to finish (~20 minutes)
- Update expt_id in `analyze_example_sim.py`
- Run analyzer via `python analyze_example_sim.py`
- Inspect `simulation_outputs` to see generated simulation results
- Done!


<details><summary><span>Generated files after successful execution of scripts</span></summary>
<p>

![img](../static/w2.1_directories_files.png)

</p>
</details>




### Week 3: Interventions in EMOD

[Lesson Week 3](https://faculty-enrich-2022.netlify.app/lessons/week-3/)

EMOD How To's:

- [Create a demographics file](https://faculty-enrich-2022.netlify.app/modules/emod-how-to/emod-how-to/#create-a-demographics-file)
- Create a climate file
- [Update config parameters](https://faculty-enrich-2022.netlify.app/modules/emod-how-to/emod-how-to/#update-config-parameters)

#### Instructions:

- Save copy of `simtools.ini` to Week-3 directory and adjust paths `<USERNAME>` with your username
- Copy the inputs and `run_example_sim.py` and `analyze_example_sim.py` from Week-2 to this folder (Week-3)
- Update interventions:
    - [TODO]
- Run and analyze simulations as you have done in previous weeks.
- Done!

<!--
<details><summary><span>Generated files after successful execution of scripts</span></summary>
<p>

![img](../static/w2.1_directories_files.png)

</p>
</details>
-->


### Week 4: Analyzers and plotters

[Lesson Week 4](https://faculty-enrich-2022.netlify.app/lessons/week-4/)

EMOD How To's:

-  Analyzers and plotters
- [TODO]

#### Instructions:

- Use the same simulation outputs from previous week (Week 3)
- Update analyzer:
    - [TODO]
- Update plots:
    - [TODO]
- Inspect generated results and figures. 
- Done!

<!--
<details><summary><span>OUTPUT FILES</span></summary>
<p>

![img](../static/w2.1_directories_files.png)

</p>
</details>
-->


### Week 5: no technical curriculum



### Week 6: Serialization

[Lesson Week 6](https://faculty-enrich-2022.netlify.app/lessons/week-6/)

EMOD How To's:

- Serialization
- [TODO]


#### Instructions:

- [TODO]


### Week 7: Sweeping and calibration

[Lesson Week 7](https://faculty-enrich-2022.netlify.app/lessons/week-7/)

EMOD How To's:

- Sweeping and calibration
- [TODO]


#### Instructions:

- [TODO]


### Week 8: Individual properties

[Lesson Week 8](https://faculty-enrich-2022.netlify.app/lessons/week-8/)

EMOD How To's:

- Individual properties
- [TODO]


#### Instructions:

- [TODO]


### Week 9: Infusing simulations with real data

[Lesson Week 9](https://faculty-enrich-2022.netlify.app/lessons/week-9/)

EMOD How To's:

- [TODO]


#### Instructions:

- [TODO]


### Week 10: no technical curriculum

### Week 11: Advanced EMOD: HBHI workflow as a complex example

[Lesson Week 11](https://faculty-enrich-2022.netlify.app/lessons/week-11/)

EMOD How To's:

- [TODO]


#### Instructions:

- [TODO]


### Week 12: Advanced EMOD: Spatial modeling in EMOD

[Lesson Week 12](https://faculty-enrich-2022.netlify.app/lessons/week-12/)

EMOD How To's:

- [TODO]


#### Instructions:

- [TODO]


### Week 13: Advanced EMOD: gene drive and reactive interventions

[Lesson Week 13](https://faculty-enrich-2022.netlify.app/lessons/week-13/)

EMOD How To's:

- [TODO]


#### Instructions:

- [TODO]


### Week 14: HPC

[Lesson Week 14](https://faculty-enrich-2022.netlify.app/lessons/week-14/)

EMOD How To's:

- [TODO]


#### Instructions:

- [TODO]


### Week 15: no technical curriculum

### Week 16: no technical curriculum

