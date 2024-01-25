# Docs 

## Todo
Rename assets vis de ikke har riktig navn


| Api-kall      | Forklaring                                                                                                         
|---------------|--------------------------------------------------------------------------------------------------------------------
| Devices       | Henter enheter fra Azure AD                                                                                        
| mangedDevices | Henter enheter fra Endpoint                                                                                        
| users         | Henter alle brukerene i gruppen Intune - Alle Ansatte                                                              
| user_Devices  | Henter alle enhetene koblet til en ansatt (Dette gjørs får å komme rund "Enrolled by" og "Primary user" problemet) 
| snipe_get     | Henter alt fra et endpoint det du spesifiserer. f.eks snipe_get('Hardware')                                        
| snipe_post    | Legger til på noe på de enpointet du spsifiserer. f.eks snipe_get('Hardware')                                      
| snipe_patch   | Oppdaere noen på enpointet du har spsifisert. feks snipe_patch('Hardware')       

| Database Funksjoner | Forklaring
|---------------------|-----------------------------------------------------
| Create_db()         | Lager SQLite databasen buffer.sqlite og lager Tables
| use_db(statment, args*)| funksjon for å kunne bruke predefinerte SQL queries

| Database Tables     | Forklaring
|---------------------|------------------------------------------------------
| manufacturer        | For manufacturer navn og id fra Snipe-IT
| model               | For model navn og fra Snipe-IT
| devices             | For enheter fra Intune
| snipe_users         | Brukernavn og id fra Snipe-IT
| intune_users        | UPN fra intune og id fra Snipe-IT

| Perdefinerte SQL queries| Bruksanvisning
|-------------------------|--------------------------------------------------
| create manufacturer     | name, manufacturer_id
| create model            | name, model_id, manufacturer, manufacturer_id
| create device           | device, serial, model, model_id, manufacturer, manufacturer_id
| create snipe_users      | device, username, user_id
| create intune_users     | device, username, user_id
| get manufacturer        | name
| get model               | model
| get device              | device_id
| get device count        | 
| get count               | table
| get snipe user          | device
| get intune user         | device
| delete                  | 

| Filer                 | Forklaring                                                            |
------------------------|-----------------------------------------------------------------------|
| main.py               | Hoved script hvor alt blir hentet inn og kjørt                        |
| api_calls.py          | Alle api kallene som skal bli gjort i en egen fil                     |
| db.py                 | Alt med databasen gjøres via her                                      |


