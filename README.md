# Democracy Club to Wikidata CSV Proxy

This is a handy little script which takes a [CSV of candidates from Democracy Club](https://candidates.democracyclub.org.uk/api/docs/csv/), strips it down, and tries to look up DC IDs and map them to known Wikidata IDs representing the same objects.

This is then spat back out in a way which can be easily interpreted by the Prompts tool.

## Identifier Maps

These CSV files map Democracy Club identifiers for areas (derived from GSS codes) and political parties (derived mostly from Electoral Commission IDs) into Wikidata object identifiers.

* [CSV of Area IDs](https://github.com/jacksonj04/dc-wikidata-proxy/blob/master/maps/areas.csv)
* [CSV of Party IDs](https://github.com/jacksonj04/dc-wikidata-proxy/blob/master/maps/parties.csv)

## Examples

The following prompts on Wikidata use this CSV proxy tool.

* [2019 United Kingdom General Election](https://www.wikidata.org/wiki/User:Jacksonj04/2019_General_Election/Prompt/DC)
* [2019 EU Parliament Elections](https://www.wikidata.org/wiki/User:Jacksonj04/2019_EU_Elections/Prompt/DC)
* [2019 Leeds City Council election](https://www.wikidata.org/wiki/User:Jacksonj04/Leeds/Prompt/2019)
* [2021 Leeds City Council election](https://www.wikidata.org/wiki/User:Jacksonj04/Leeds/Prompt/2021)
