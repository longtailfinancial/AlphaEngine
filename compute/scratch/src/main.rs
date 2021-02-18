#![feature(async_stream)]
use chrono::NaiveDate;
use ndarray::prelude::*;
use serde::Deserialize;
use walkdir::WalkDir;

use async_stream::stream;
use futures_util::future::join_all;
use futures_util::pin_mut;
use futures_util::stream::Stream;
use futures_util::stream::StreamExt;

use std::collections::HashMap;
use std::error::Error;

use tokio::fs::File;
use tokio::io::{AsyncRead, AsyncWrite};
use std::io::Read;

#[derive(Debug, Deserialize)]
struct Record {
    date: String,
    open: f64,
    high: f64,
    low: f64,
    close: f64,
    volume: usize,
}

#[tokio::main]
async fn main() {
    // let stream = load_files("../../../prices").await;
    let stream = load_files(".").await;
    pin_mut!(stream);

    while let Some(file) = stream.next().await {
        match file {
            Ok((symbol, records)) => {
                // println!(
                //     "\n--- {} ---\n{:?}",
                //     symbol,
                //     records.iter().take(5).collect::<Vec<_>>()
                // );
            }
            Err(why) => eprintln!("Error: {:?}", why),
        }
    }
}

async fn load_files<P: Into<String>>(
    path: P,
) -> impl Stream<Item = Result<(String, Vec<Record>), tokio::io::Error>> {
    stream! {
        for entry in WalkDir::new(&path.into())
            .min_depth(1)
                .max_depth(3)
                .into_iter()
                .filter_map(|e| e.ok())
                .filter(|e| {
                    e.file_name()
                        .to_string_lossy()
                        .to_string()
                        .ends_with(".csv")
                })
        {
            let file_name = entry.file_name().to_string_lossy().to_string();
            let symbol = file_name.split(".csv").next().unwrap_or("N/A").to_string();

            yield load_file(symbol, entry.path()).await;
        }
    }
}

async fn load_file(symbol: String, path: &std::path::Path) -> Result<(String, Vec<Record>), tokio::io::Error> {
    let file = File::open(path).await?;

    let mut std_file = file.into_std().await;

    let mut string = String::new();

    std_file.read_to_string(&mut string)?;

    print!("Raw CSV: {}", string);

    let mut rdr = csv::Reader::from_reader(string.as_bytes());
    rdr.set_headers(csv::StringRecord::from(vec![
        "date", "open", "high", "low", "close", "volume",
    ]));

    let records = rdr
        .deserialize()
        .filter_map(|r| match r {
            Ok(record) => {
                println!("Valid Record: {:?}", record);
                Some(record)
            },
            Err(why) => {
                eprintln!(
                    "Failed to read record for {}: {:?}",
                    symbol.to_string(),
                    why
                );
                None
            }
        })
        .collect::<Vec<_>>();

    Ok((symbol.to_string(), records))
}

#[cfg(test)]
mod tests {
    use crate::load_file;

    #[tokio::test]
    async fn test_load_csv() {
        let result = load_file("AAPL".to_string(), std::path::Path::new("./test.csv")).await;
        assert!(result.is_ok());
        let (symbol,records) = result.unwrap();

        assert_eq!(symbol, "AAPL".to_string());
    }
}