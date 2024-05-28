import { Camera } from "@/components/content/camera"
import { useNavigate } from "@solidjs/router";
import { createEffect } from "solid-js";

export default () => {

    const navigate = useNavigate();

    createEffect(() => {
        const handleResize = () => {
            if (window.innerWidth >= 768) {  // Replace 600 with the desired viewport width
                navigate('/');
            }
        };

        // Add event listener
        window.addEventListener('resize', handleResize);

        // Check the viewport size initially
        handleResize();

        // Cleanup event listener on component unmount
        return () => {
            window.removeEventListener('resize', handleResize);
        };
    });

    return (
        <div class="w-full max-w-[500px]">
            <Camera />
        </div>
    )
}