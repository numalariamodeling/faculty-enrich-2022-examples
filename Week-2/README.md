### Example code for Week 2

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

