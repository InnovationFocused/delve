import sys
import logging
import inspect
from urllib.parse import urlparse
from dataclasses import dataclass
from multiprocessing import (
    Process,
    Queue,
)

from pony.orm import (
    db_session,
    commit,
    select,
)
# from apscheduler.schedulers.blocking import BlockingScheduler
# from apscheduler.triggers.interval import IntervalTrigger
# from apscheduler.triggers.cron import CronTrigger
# from apscheduler.triggers.date import DateTrigger

# from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

from .models import (
    Event,
    Tag,
)
from .config import get_obj_from_name
from pydantic import BaseModel

class InputConfigStanzaSchema(BaseModel):
    type: str
    index: str
    host: str
    source: str
    sourcetype: str
    extractions: list[str]
    transformations: list[str]
    filters: list[str]
    tags: list[str]

    @classmethod
    def get_field_names(cls,alias=False):
        return list(cls.schema(alias).get("properties").keys())


def handle_inputs(config: dict, handler_map: dict) -> int:
    log = logging.getLogger(__name__)
    log.debug(f"Found config: '{config}'")

    standard_field_names = InputConfigStanzaSchema.get_field_names()
    log.debug(f"Got standard_field_names: {standard_field_names}")
    inputs = {}
    for name, settings in config.items():
        log.debug(f"Found Input {name}: {settings}")
        # The below line removes the standard fields from settings so
        # we can pass what is left to the plugin
        kwargs = {k: settings.pop(k) for k in standard_field_names}
        # We need to add name to settings
        log.debug(f"Found standard fields: {kwargs}")
        parsed_settings = InputConfigStanzaSchema(**kwargs)
        log.debug(f"Found parsed_settings: {parsed_settings}")
        handler_cls_name = handler_map[parsed_settings.type]
        log.debug(f"Found handler_cls_name: {handler_cls_name}")
        handler = get_obj_from_name(handler_cls_name)
        log.debug(f"Found handler: {handler}")
        inputs[name] = (handler(**settings), parsed_settings)

        # We need to make sure that the tags exist
        with db_session():
            for tag_name in parsed_settings.tags:
                log.debug(f"Found tag_name: '{tag_name}'")
                tag = Tag.get(name=tag_name)
                if tag is None:
                    log.debug(f"Tag '{tag_name}' does not exist. Creating.")
                    tag = Tag(name=tag_name)
            commit()
    
    # Now we can actually get the data
    while inputs:
        for name, (handler, settings) in inputs.copy().items():
            log.debug(f"Polling {name}:{handler} for inputs")
            try:
                raw = next(handler)
                log.debug(f"Found event: {raw}")
            except StopIteration:
                log.info(f"Input {name}:{handler} stopped producing events.")
                del inputs[name]
            text = raw
            if any(get_obj_from_name(f)(raw) for f in settings.filters):
                # If any filter matches, skip that event
                continue
            for transformation_name in settings.transformations:
                log.debug(f"Applying transformation: {transformation}: {text}")
                transformation = get_obj_from_name(transformation_name)
                log.debug(f"Found transformation callable: {transformation}")
                text = transformation(text)
                log.debug(f"Applied transformation: {transformation}: {text}")
            extracted_fields = {}
            for extraction_name in settings.extractions:
                log.debug(f"Extracting fields using {extraction_name}")
                extraction = get_obj_from_name(extraction_name)
                log.debug(f"Found extraction callable: {extraction}")
                extracted = extraction(text)
                log.debug(f"Fields extracted using {extraction}: {extracted}")
                extracted_fields.update(extracted)
                log.debug(f"All fields extracted so far: {extracted_fields}")
            with db_session():
                tags = select(tag for tag in Tag if tag.name in settings.tags)
                log.debug(f"Found tags: {tags}")
                e = Event(
                    raw=raw,
                    text=text,
                    index=settings.index,
                    host=settings.host,
                    source=settings.source,
                    sourcetype=settings.sourcetype,
                    extracted_fields=extracted_fields,
                    tags=tags,
                )
                commit()
    return 0

# def add_job(target, trigger, scheduler, conf):
#     log = logging.getLogger(__name__)
#     log.debug(f"Found target: '{target}'")
#     log.debug(f"Found trigger: '{trigger}'")
#     log.debug(f"Found scheduler: '{scheduler}'")
#     log.debug(f"Found conf: '{conf}'")
#     if trigger["type"] == "startup":
#         job =  scheduler.add_job(
#             func=target,
#             args=conf.get("args"),
#             kwargs=conf.get("kwargs"),
#         )
#     elif trigger["type"] == "interval":
#         job =  scheduler.add_job(
#             func=target,
#             trigger=IntervalTrigger(**{k: v for k, v in trigger.items() if k != "type"}),
#             args=conf.get("args"),
#             kwargs=conf.get("kwargs"),
#         )
#     elif trigger["type"] == "cron":
#         job =  scheduler.add_job(
#             func=target,
#             trigger=CronTrigger(**{k: v for k, v in trigger.items() if k != "type"}),
#             args=conf.get("args"),
#             kwargs=conf.get("kwargs"),
#         )
#     elif trigger["type"] == "date":
#         job =  scheduler.add_job(
#             func=target,
#             trigger=DateTrigger(**{k: v for k, v in trigger.items() if k != "type"}),
#             args=conf.get("args"),
#             kwargs=conf.get("kwargs"),
#         )
#     return job


# def handle_inputs(config: dict) -> None:
#     log = logging.getLogger(__name__)
#     log.debug(f"Found config: '{config}'")
#     # log.debug(f"Found handler_map: '{handler_map}'")
    
#     scheduler = BlockingScheduler()
#     def listener(event):
#         if not event.exception:
#             job = scheduler.get_job(event.job_id)
#             log.debug(f"Found job: '{job}'")
#             result = event.retval
#             log.debug(f"Found result: '{result}'")
#             tag_names = result.pop("tags")
#             log.debug(f"Found tag_names: {type(tag_names)}('{tag_names}')")
#             with db_session():
#                 e = Event(
#                     tags=select(tag for tag in Tag if tag.name in tag_names),
#                     **result,
#                 )
#                 commit()
        
#     scheduler.add_listener(listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
#     inputs = {}
#     for name, conf in config.items():
#         if name in inputs:
#             raise ValueError(f"name: '{name}' is a duplicate. '{inputs[name]}'")
#         target = conf.get("target", None)
#         job_factory = conf.get("job_factory", None)
#         with db_session():
#             for tag_name in conf.get("tags", tuple()):
#                 log.debug(f"Found tag_name: '{tag_name}'")
#                 tag = Tag.get(name=tag_name)
#                 if tag is None:
#                     log.debug(f"Tag '{tag_name}' does not exist. Creating.")
#                     tag = Tag(name=tag_name)
#             commit()

#         if target:
#             target = get_obj_from_name(target)
#             trigger = conf.get("trigger", None)
#             if trigger is None:
#                 raise ValueError("Input '{name}' defines a target but not a trigger")
#             job = add_job(target, trigger, scheduler, conf)
#             inputs[name] = job

#         elif job_factory:
#             job_factory = get_obj_from_name(job_factory)
#             inputs[name] = []
#             jobs = job_factory(conf)
#             for job in jobs():
#                 _job = add_job(job["target"], job["trigger"], scheduler,  job["conf"])
#                 inputs[name].append(_job)
#     scheduler.start()


# def handle_inputs(config: dict, handler_map: dict):
#     log = logging.getLogger(__name__)
#     log.debug(f"Found config: '{config}'")
#     log.debug(f"Found handler_map: '{handler_map}'")
    
#     inputs = {}
#     daemon_inputs = {}
#     for name, conf in config.items():
#         log.debug(f"Found name: '{name}', conf: '{conf}'")
#         if name in inputs:
#             raise ValueError(f"Duplicate input: '{name}'")
#         parsed_name = urlparse(name)
#         log.debug(f"Found parsed_name: '{parsed_name}'")

#         handler_cls_name = handler_map.get(parsed_name.scheme, None)
#         if handler_cls_name is None:
#             raise ValueError(f"No handler found for {parsed_name.proto}")
#         log.debug(f"Found handler_cls_name: '{handler_cls_name}'")
#         handler_cls = get_obj_from_name(handler_cls_name)
#         log.debug(f"Found handler_cls: '{handler_cls}'")

#         tag_names = conf.get("tags")
#         log.debug(f"Found tag_names: '{tag_names}'")

#         extractions = conf.get("extractions")
#         extractions = [get_obj_from_name(extraction) for extraction in extractions]

#         with db_session():
#             for tag_name in tag_names:
#                 log.debug(f"Found tag_name: '{tag_name}'")
#                 tag = Tag.get(name=tag_name)
#                 log.debug(f"Result for tag.name=='{tag_name}': {tag}")
#                 if tag is None:
#                     log.debug(f"Tag '{tag_name}' does not exist. Creating.")
#                     tag = Tag(name=tag_name)
#                 commit()
#                 # tags.append(tag)

#         if issubclass(handler_cls, Process):
#             q = Queue()
#             # log.debug(f"HERE:  {conf['credentials']}")
#             daemon_inputs[name] = handler_cls(parsed_name, conf, q)

#             class _iter:
#                 def __init__(self, conf):
#                     self.conf = conf

#                 def __iter__(self):
#                     return self
                
#                 def __next__(self):
#                     return q.get()

#             inputs[name] = (_iter(conf), tag_names, extractions)
#             daemon_inputs[name].start()
#             continue

#         inputs[name] = (handler_cls(parsed_name, conf), tag_names, extractions)
#         log.debug(f"Found input: '{name}': '{inputs[name]}'")
#     while inputs:
#         for name, (handler, tag_names, extractions) in inputs.copy().items():
#             log.debug(f"Polling for event from input '{name}': '{handler}'. Tags: {tag_names}, Extractions: {extractions}")
#             try:
#                 event = next(handler)
#             except StopIteration:
#                 log.info(f"Input '{name}' has stopped producing events. (It raised a StopIteration Exception). Removing input.")
#                 del inputs[name]
#             if isinstance(event, str):
#                 event = event.strip()
#                 if not event:
#                     continue
#                 log.debug(f"Found event: '{event}'")
#                 extracted_fields = {}
#                 for extraction in extractions:
#                     extracted_fields.update(extraction(event))
#                 with db_session():
#                     # tags = [.first() for tag in tag_names]
#                     # tags = select(tag for tag in Tag if tag.name in tag_names)
#                     try:
#                         tags = select(tag.name for tag in Tag)
#                     except:
#                         log.exception("An unhandled exception occurred.")
#                         sys.exit(0)
#                     log.debug(f"Tags: {tags}")
#                     e = Event(
#                         raw=event,
#                         text=event,
#                         index=handler.conf.get("index"),
#                         host=handler.conf.get("host"),
#                         source=handler.conf.get("source"),
#                         sourcetype=handler.conf.get("sourcetype"),
#                         extracted_fields=extracted_fields,
#                         tags=tags,
#                     )
#                     commit()
#             elif inspect.isgeneratorfunction(event):
#                 for _event in event:
#                     _event = _event.strip()
#                     if not _event:
#                         continue
#                     log.debug(f"Found event: '{_event}'")
#                     extracted_fields = {}
#                     for extraction in extractions:
#                         extracted_fields.update(extraction(_event))
#                     with db_session():
#                         # tags = [.first() for tag in tag_names]
#                         # tags = select(tag for tag in Tag if tag.name in tag_names)
#                         try:
#                             tags = select(tag.name for tag in Tag)
#                         except:
#                             log.exception("An unhandled exception occurred.")
#                             sys.exit(0)
#                         log.debug(f"Tags: {tags}")
#                         e = Event(
#                             raw=_event,
#                             text=_event,
#                             index=handler.conf.get("index"),
#                             host=handler.conf.get("host"),
#                             source=handler.conf.get("source"),
#                             sourcetype=handler.conf.get("sourcetype"),
#                             extracted_fields=extracted_fields,
#                             tags=tags,
#                         )
#                         commit()
#                 else:
#                     del inputs[name]