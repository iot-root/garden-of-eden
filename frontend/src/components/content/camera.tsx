import Padding from "@/components/containers/padding"
import { Add } from "@/components/ui/add"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { CaptureImages, DeleteImage, GetImage, ListImages } from "@/endpoints/camera"
import { setModalContent, toggleModal } from "@/root/stores/modal"
import { Detail, H1 } from "@/typography/heading"
import { Index, Match, Suspense, Switch, createEffect, createResource, createSignal } from "solid-js"
import { Oval } from 'solid-spinner'
import { Card } from "../ui/card"


const ImageView = (props) => {

    const handleDeleteImage = async (filename, refetch, toggleModal) => {
        await DeleteImage(filename)
        await refetch()
        toggleModal(false)
    }

    return (
        <div class="h-[50vh] w-[50vh] p-10 bg-white rounded-sm">
            <div class="">
                <img src={props.image.url} class="object-cover mb-4"></img>
                <div class="w-full flex flex-row justify-start">
                    <Button variant="destructive" onClick={() => handleDeleteImage(props.image.filename, props.refetch, props.toggleModal)} >Delete</Button>
                </div>
            </div>
        </div>
    )
}

export const Camera = () => {
    const [images, setImages] = createSignal([]);
    const [isCaptureLoading, setIsCaptureLoading] = createSignal(false);
    const [images_filenames, { refetch }] = createResource(ListImages);

    createEffect(async () => {
        if (images_filenames.loading) {
            console.log("Loading image filenames...");
            return;
        }

        if (images_filenames.error) {
            console.error("Error loading images:", images_filenames.error);
            return;
        }

        setImages([]);

        const loadedImages = await Promise.all(
            images_filenames().value?.map(async (filename) => {
                const response = await GetImage(filename);
                return { "url": response, "filename": filename };
            })
        );

        // sort images
        loadedImages.sort((a, b) => {
            return b.filename.localeCompare(a.filename);
        })

        // Update images state with new data
        setImages(loadedImages);
    });

    const handleCapture = async () => {
        setIsCaptureLoading(true)
        await CaptureImages()
        setIsCaptureLoading(false)
        refetch()
    }

    const onImageClick = (image, refetch, toggleModal) => {
        toggleModal(true)
        setModalContent(() => (
            <ImageView image={image} refetch={refetch} toggleModal={toggleModal} />
        ))
    }

    return (
        <Padding>
            <div class="flex flex-row justify-between items-center">
                <H1>Camera</H1>
                <Switch>
                    <Match when={!isCaptureLoading()}>
                        <button onClick={handleCapture}>
                            <Add label="Capture" />
                        </button>

                    </Match>
                    <Match when={isCaptureLoading()}>
                        <Oval color="gray" />
                    </Match>
                </Switch>
            </div>

            <Detail class="mb-4">Most recent photos appear first.</Detail>
            <Card>
                <div class="flex flex-row flex-wrap gap-1">
                    <Suspense fallback={<Detail>Loading...</Detail>}>
                        <Switch>
                            <Match when={images_filenames()?.error}>
                                <Detail error>{`${String(images_filenames()?.error).slice(0, 30)}...`}</Detail>
                            </Match>

                            <Match when={images().length == 0 && images_filenames()?.loading}>
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
                                    Object.entries(images_filenames().value).length == 0 ? <Detail>No images.</Detail> : ""
                                }

                                <Index each={images()}>
                                    {(image, i) => {
                                        return (
                                            <div class="w-20 h-20 bg-zinc-200 rounded-[8px]">
                                                <button class="h-full" onClick={() => onImageClick(image(), refetch, toggleModal)}>
                                                    <img src={image().url} class="object-cover h-full"></img>
                                                </button>
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