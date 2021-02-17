use vulkano::instance::Instance;
use vulkano::instance::InstanceExtensions;

use vulkano::instance::PhysicalDevice;

use vulkano::device::Device;
use vulkano::device::DeviceExtensions;
use vulkano::device::Features;
use vulkano::device::Queue;

use std::sync::Arc;

/// Initialize Vulkan and get a Device and Queue
pub fn initialize_vulkan() -> (Arc<Device>, Arc<Queue>){
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
        Device::new(physical, &Features::none(), &DeviceExtensions::none(),
            [(queue_family, 0.5)].iter().cloned()).expect("failed to create device")
    };

    let queue = queues.next().unwrap();

    (device, queue)
}

mod shaders;

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
