use vulkano::instance::Instance;
use vulkano::instance::InstanceExtensions;

use vulkano::instance::PhysicalDevice;

use vulkano::device::Device;
use vulkano::device::DeviceExtensions;
use vulkano::device::Features;
use vulkano::device::Queue;

use vulkano::buffer::{BufferUsage, CpuAccessibleBuffer};
use vulkano::command_buffer::{AutoCommandBufferBuilder, CommandBuffer};

use vulkano::pipeline::ComputePipeline;

use vulkano::descriptor::descriptor_set::PersistentDescriptorSet;
use vulkano::descriptor::PipelineLayoutAbstract;

use vulkano::sync::GpuFuture;

use std::sync::Arc;

/// Initialize Vulkan and get a Device and Queue
pub fn initialize_vulkan() -> (Arc<Device>, Arc<Queue>) {
    // Create a vulkan instance
    let instance =
        Instance::new(None, &InstanceExtensions::none(), None).expect("failed to create instance");

    // Enumerate physical devices
    let physical = PhysicalDevice::enumerate(&instance)
        .next()
        .expect("no device available");

    // Find queue family
    let queue_family = physical
        .queue_families()
        .find(|&q| q.supports_graphics())
        .expect("couldn't find a graphical queue family");

    // Create device
    let (device, mut queues) = {
        Device::new(
            physical,
            &Features::none(),
            &DeviceExtensions::none(),
            [(queue_family, 0.5)].iter().cloned(),
        )
        .expect("failed to create device")
    };

    let queue = queues.next().unwrap();

    (device, queue)
}

pub fn run_shader() {
    let (device, queue) = initialize_vulkan();

    // Create data buffer
    let data_iter = 0..65536;
    let data_buffer =
        CpuAccessibleBuffer::from_iter(device.clone(), BufferUsage::all(), false, data_iter)
            .expect("failed to create buffer");

    // Compile SPIRV and load GLSL shader
    let shader = shaders::cs::Shader::load(device.clone()).expect("Failed to create shader module");

    // Load shader into compute pipeline
    let compute_pipeline = Arc::new(
        ComputePipeline::new(device.clone(), &shader.main_entry_point(), &(), None)
            .expect("failed to create compute pipeline"),
    );

    // Create a descriptor set
    let layout = compute_pipeline.layout().descriptor_set_layout(0).unwrap();
    let set = Arc::new(
        PersistentDescriptorSet::start(layout.clone())
            .add_buffer(data_buffer.clone())
            .unwrap()
            .build()
            .unwrap(),
    );

    // Create our command buffer
    let mut builder = AutoCommandBufferBuilder::new(device.clone(), queue.family()).unwrap();
    builder.dispatch([1024, 1, 1], compute_pipeline.clone(), set.clone(), ()).unwrap();
    let command_buffer = builder.build().unwrap();

    // Submit to GPU
    let finished = command_buffer.execute(queue.clone()).unwrap();

    // Wait for it to complete
    finished.then_signal_fence_and_flush().unwrap()
            .wait(None).unwrap();

    // Verify result
    let content = data_buffer.read().unwrap();
    for (n, val) in content.iter().enumerate() {
        assert_eq!(*val, n as u32 * 12);
    }

    println!("Everything succeeded!");
}


mod shaders;

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
