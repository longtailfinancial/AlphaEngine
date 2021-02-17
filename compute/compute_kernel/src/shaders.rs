pub mod alpha_engine {
    vulkano_shaders::shader! {
        ty: "compute",
        path: "./shaders/alpha_engine.glsl"
    }
}
