use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

use loader::{load_files, pin_mut, Stream, StreamExt};

use std::collections::HashMap;

#[pyclass]
struct PyRecord {
    date: String,
    open: f64,
    high: f64,
    low: f64,
    close: f64,
    volume: usize,
}

impl From<loader::Record> for PyRecord {
    fn from(rec: loader::Record) -> Self {
        let loader::Record { date, open, high, low, close, volume } = rec;
        Self {
            date, open, high, low, close, volume
        }
    }

}

#[pyclass]
struct PyRecordList {
    records: Vec<(String, Vec<PyRecord>)>
}



#[pyfunction]
/// Loads the Dataset
pub fn load_dataset(py: Python, path: String) -> PyResult<PyObject> {
    pyo3_asyncio::tokio::into_coroutine(py, async move {
        let mut vec = Vec::new();

        let s = load_files(path).await;
        pin_mut!(s);
        while let Some(file) = s.next().await {
            if let Ok((symbol, records)) = file {
                vec.push((symbol, records.into_iter().map(|r| r.into()).collect::<Vec<PyRecord>>()));
            }
        }

        Ok(Python::with_gil(|py| {
            PyRecordList {
                records: vec
            }.into_py(py)
        }))
    })
}
