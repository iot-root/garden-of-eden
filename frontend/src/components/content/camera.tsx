import Padding from "@/components/containers/padding"
import { Add } from "@/components/ui/add"
import { Skeleton } from "@/components/ui/skeleton"
import { CaptureImages, GetImage, ListImages } from "@/endpoints/camera"
import { Detail, H1 } from "@/typography/heading"
import { Index, Match, Suspense, Switch, createEffect, createResource, createSignal } from "solid-js"
import { Card } from "../ui/card"
export const Camera = () => {
    const [images, setImages] = createSignal([]);
    const [images_filenames, { refetch }] = createResource(ListImages);

    // Effect to fetch image data whenever filenames are updated
    createEffect(async () => {
        if (images_filenames.loading) {
            console.log("Loading image filenames...");
            return;
        }

        if (images_filenames.error) {
            console.error("Error loading images:", images_filenames.error);
            return;
        }

        // Clear previous images
        setImages([]);

        // Load each image and update the state
        const loadedImages = await Promise.all(
            images_filenames().value?.map(async (filename) => {
                const response = await GetImage(filename);
                return response;
            })
        );

        // Update images state with new data
        setImages(loadedImages);
    });

    const handleCapture = async () => {
        await CaptureImages()
        refetch()
    }

    return (
        <Padding>
            <div class="flex flex-row justify-between items-center">
                <H1>Camera</H1>
                <button onClick={handleCapture}>
                    <Add label="Capture" />
                </button>
            </div>

            <Detail class="mb-4">Most recent photos appear first.</Detail>
            <Card>
                <div class="flex flex-row flex-wrap gap-1">
                    <Suspense fallback={<Detail>Loading...</Detail>}>
                        <Switch>
                            <Match when={images_filenames()?.error}>
                                <Detail error>{`${String(images_filenames()?.error).slice(0, 30)}...`}</Detail>
                            </Match>

                            <Match when={images().length == 0}>
                                <Skeleton class="w-20 h-20" />
                                <Skeleton class="w-20 h-20" />
                                <Skeleton class="w-20 h-20" />
                                <Skeleton class="w-20 h-20" />
                                <Skeleton class="w-20 h-20" />
                                <Skeleton class="w-20 h-20" />
                                <Skeleton class="w-20 h-20" />
                                <Skeleton class="w-20 h-20" />
                            </Match>

                            <Match when={images_filenames()}>
                                {
                                    Object.entries(images_filenames()).length == 0 ? <Detail>No images.</Detail> : ""
                                }

                                <Index each={images()}>
                                    {(image, i) => {
                                        return (
                                            <div class="w-20 h-20 bg-zinc-200 rounded-[8px]">
                                                <img src={image()} class="object-cover h-full"></img>
                                            </div>)
                                    }}
                                </Index>
                            </Match>
                        </Switch>
                    </Suspense>

                </div>
            </Card>
        </Padding>
    )
}