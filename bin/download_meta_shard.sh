#!/bin/bash

# create directory
mkdir 20200705v1
mkdir 20200705v1/full/
mkdir 20200705v1/full/metadata/

wget -O 20200705v1/full/metadata/metadata_0.jsonl.gz 'https://ai2-s2-s2orc.s3.amazonaws.com/20200705v1/full/metadata/metadata_0.jsonl.gz?AWSAccessKeyId=AKIA5BJLZJPW4OD5EQ2P&Signature=uPfuXHEVYI39hwwibohK1CcK5Q0%3D&Expires=1654817320'

gzip -fd 20200705v1/full/metadata/metadata_0.jsonl.gz