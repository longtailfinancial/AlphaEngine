use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

use loader::{load_files, pin_mut, Stream, StreamExt};

mod loader_binds;
use loader_binds::{load_dataset, PyRecord, PyRecordList};

/// A Python module implemented in Rust.
#[pymodule]
fn ack(py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyRecord>()?;
    m.add_class::<PyRecordList>()?;

    m.add_function(wrap_pyfunction!(load_dataset, m)?)?;

    Ok(())
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
