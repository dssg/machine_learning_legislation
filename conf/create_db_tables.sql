create table documents (
id serial primary key,
date date,
version varchar(100),
congress_meta_document integer
);

create table congress_meta_document
(
id serial primary key,
bill boolean,
sunlight_id varchar(32),
congress integer,
number varchar(100),
senate boolean
);

create table sponsors
(
candidate_earmark_id integer,
sponsor varchar(128)
);

create table candidate_earmarks
(
id serial primary key,
congress integer,
chamber varchar(10),
document_type varchar(6),
city varchar(128),
state varchar(2),
county varchar(128),
row varchar(2048),
row_offset integer,
row_length integer,
score float
);



create table entities
(
id serial primary key,
entity_text varchar(256),
entity_type varchar(100),
entity_offset integer,
entity_length integer,
entity_inferred_name varchar(512),
source varchar(64),
document_id integer,
entity_url varchar(512)
);

create table bill_reports
(
id serial primary key,
bill_id integer,
report_id integer
);

create table earmarks
(
earmark_id integer primary key,
earmark_code varchar(256),
agency varchar(512),
bureau varchar(512),
account varchar(512),
program varchar(512),
enacted_year integer,
short_description varchar(512),
full_description varchar(2048),
earmark_type varchar(512),
spendcom varchar(512),
recipient varchar(512)
);

create table earmark_documents
(
id serial primary key,
earmark_id integer,
document_id integer,
page_number varchar(256),
excerpt varchar(4096),
inferred_offset integer,
inferred_length integer,
matching_entity_id integer
);

create table organization_allocation
(
id serial primary key,
organization_entity_id integer not null,
allocation_entity_id integer not null
);

create table entity_wikipedia_page
(
id serial primary key,
entity_id int,
wikipedia_page varchar(512)
);

create table earmark_document_matched_entities
(
earmark_document_id int,
matched_entity_id int,
manual_match boolean default False,
primary key (earmark_document_id, matched_entity_id)
);


create table matching_labels
(
    earmark_id integer,
    document_id integer,
    entity_id integer,
    match boolean default False
);
