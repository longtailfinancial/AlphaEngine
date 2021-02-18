use pyo3::prelude::*;

fn main() {
    Python::with_gil(|py| {
        pyo3_asyncio::with_runtime(py, || {
            println!("PyO3 Asyncio Initialized!");
            Ok(())

        })
        .map_err(|e| {
            e.print_and_set_sys_last_vars(py);  

        })
        .unwrap();

        })

}
