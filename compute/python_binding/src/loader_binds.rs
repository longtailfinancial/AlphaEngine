use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

use loader::{load_files, pin_mut, Stream, StreamExt};

use std::collections::HashMap;

#[pyclass]
pub struct PyRecord {
    pub date: String,
    pub open: f64,
    pub high: f64,
    pub low: f64,
    pub close: f64,
    pub volume: usize,
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
pub struct PyRecordList {
    pub records: Vec<(String, Vec<PyRecord>)>
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
