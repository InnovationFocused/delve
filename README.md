# delve

## a simple, but effective analytics platform

Delve is an analytics platform focused on:

* Simplicity
* Loading Data
* Exploring Data
* Transforming Data
* Visualizing Data
* Exporting Data

## Installation

Install with the following command:

```
$ pip install git+https://github.com/InnovationFocused/delve
```

## Introduction

The following are the major concepts of delve:

* InputHandlers
* Event Transformations
* Field Extractions
* Search Commands
* Dashboards

## Input Handlers

Input Handlers are Python generators which produce events for indexing.

You can use one of the built-in InputHandlers or you can write your own.

The following are the built-in Input Handlers:

* HTTPInputHandler
* PythonInputHandler
* FileInputHandler

To write your own you can start by reading the [documentation](TODO: Put link here)

## Event Transformations

Transformations are Python callables which are called during indexing. Transformations accept
an event as a single argument (a str) and return a str. The str which is returned is then used 
as the text of the event.

The following are the built-in Transformations:

* 

## Field Extractions

FieldExtractions are Python callables which are called during indexing. FieldExtractions accept
an event as a single argument (a str) and return a dict of extracted fields. These fields are
used to populate the extracted_fields column for the event.

The following are the built-in FieldExtractions:

* JSONFieldExtractor
* YAMLFieldExtractor
* XMLFieldExtractor
* TOMLFieldExtractor

## Search Commands

SearchCommands are Python callables which are called during a search. SearchCommands typically
accept two arguments:

* argv - A list of arguments (produced by `shlex.split`)
* results - a list of dicts representing Events or a Pandas DataFrame

Search commands can have the following behavior:

* Return a list of dicts
* Yield dicts one at a time
* Return a Pandas DataFrame

The following are the built-in search commands:

* add-field - adds a field from the event to `extracted_fields`
* drop - Removes a field from the result
* extract-json -  Extracts fields from JSON formatted events
* extracted - drops all fields except extracted_fields and makes top-level keys the columns of the events
* linechart - draw line-charts based on data from the current events
* rex - Use regular expressions to extract fields
* save - persist changes to events to the database
* search - Populates a search (if used as the first search command) or filters a list of events
* to-df - converts a list of dicts to a Pandas DataFrame

## Dashboards

Dashboards are streamlit apps which are used to make the most out of your search results.

Currently, The search dashboard is the only built-in dashboard

