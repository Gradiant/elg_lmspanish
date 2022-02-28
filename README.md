# lm-spanish

Language models for the spanish language that are part of the MarIA project. An updated revision of those models can be found [here](https://github.com/PlanTL-GOB-ES/lm-spanish). More concretely this project uses the RoBERTa-base-BNE for SQAC.

# Usage


## Install
```
sh docker-build.sh
```
## Run
```
docker run --rm -p 0.0.0.0:8866:8866 --name elg_lmspanish:1.0 elg_lmspanish
```

## Use

Use CURL to make a API request. Use the proper question/context order. The first 'content' field should be the context, and the second the question.

```
curl -X POST http://0.0.0.0:8866/process -H 'Content-Type: application/json' -d '{"type": "structuredText","texts":[{"content": "Tengo 19 años y me llamo Maria."}, {"content": "Cuál es su nombre?"}]}'
```


Result:

```
{"response":{
"type":"annotations",
"annotations":{
   "answers":[{"start":25,
               "end":30,
               "features":{
                           "answer":"Maria",
                           "score":0.999973714351654}
                           }]}}}

```

# Test
In the folder `test` you have the files for testing the API according to the ELG specifications.
It uses an API that acts as a proxy with your dockerized API that checks both the requests and the responses.
For this follow the instructions:

1) Launch the test: `sudo docker-compose --env-file lmspanish.env up`

2) Make the requests, instead of to your API's endpoint, to the test's endpoint:
   ```
     curl -X POST http://0.0.0.0:8866/processText/service -H 'Content-Type: application/json' -d '{"type": "structuredText","texts":[{"content": "Tengo 19 años y me llamo Maria."}, {"content": "Cuál es su nombre?"}]}'
   ```
   
3) If your request and the API's response is compliance with the ELG API, you will receive the response.
   1) If the request is incorrect: Probably you will don't have a response and the test tool will not show any message in logs.
   2) If the response is incorrect: You will see in the logs that the request is proxied to your API, that it answers, but the test tool does not accept that response. You must analyze the logs.

# Citation
The original work of this tool is:
- https://github.com/PlanTL-GOB-ES/lm-spanish
 ```
@misc{gutierrezfandino2021spanish,
      title={Spanish Language Models}, 
      author={Asier Gutiérrez-Fandiño and Jordi Armengol-Estapé and Marc Pàmies and Joan Llop-Palao and Joaquín Silveira-Ocampo and Casimiro Pio Carrino and Aitor Gonzalez-Agirre and Carme Armentano-Oller and Carlos Rodriguez-Penagos and Marta Villegas},
      year={2021},
      eprint={2107.07253},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```
- For questions regarding this work, contact Asier Gutiérrez-Fandiño (<plantl-gob-es@bsc.es>)
