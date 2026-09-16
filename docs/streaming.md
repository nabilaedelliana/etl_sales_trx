# Streaming Pipeline

## Overview

This project includes an optional simple real-time streaming pipeline using a Python dummy transaction generator.

The pipeline continuously generates dummy transactions, aggregates the number of transactions per minute, and outputs the aggregated result to the console.

## Pipeline Architecture

```text
Dummy Transaction Generator
            |
            v
       Python Loop
            |
            v
 Aggregate Transaction Count
         Per Minute
            |
            v
      Console Output
```

## Pipeline Components
1. Source — Dummy Transaction Generator

The pipeline generates dummy transaction events continuously using Python.

Each generated transaction contains:

transaction_id
customer_id
amount
timestamp

The generator uses randomly generated transaction values to simulate incoming transaction events.

2. Processing — Aggregate Transaction Count Per Minute

Each transaction timestamp is truncated to the minute.

Transactions generated within the same minute are counted together.

For example:
`2026-09-16 15:51 | Transactions: 43`
This indicates that 43 transactions were generated during that minute.

3. Sink — Console Output

The aggregated transaction count is written to the console.

The pipeline does not persist the streaming results to a database because this implementation is intended as a lightweight demonstration of a real-time processing pipeline.

## Implementation

The streaming pipeline is implemented in:

`scripts/streaming_transaction.py`

Run the pipeline with:

`python scripts/streaming_transaction.py`

The pipeline runs continuously until it is stopped using:

`Ctrl + C`
## Design Choice

A Python loop was selected instead of Kafka for this optional streaming implementation to keep the pipeline lightweight and easy to run locally.

The implementation demonstrates the core streaming concepts:

Continuous event generation
Event timestamp handling
Time-based aggregation
Real-time console output

For a production environment, the same processing pattern could be implemented using a streaming platform such as Kafka and a persistent downstream sink.
