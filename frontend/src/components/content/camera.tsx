import Padding from "@/components/containers/padding"
import { Add } from "@/components/ui/add"
import { ListImages } from "@/endpoints/camera"
import { Detail, H1 } from "@/typography/heading"
import { createResource } from "solid-js"
import { Card } from "../ui/card"

export const Camera = () => {
    const [images_filenames, { refetch: refetchSchedules }] = createResource(ListImages)


    return (
        <Padding>
            <div class="flex flex-row justify-between items-center">
                <H1>Camera</H1>
                <Add label="Capture" />
            </div>
            <Detail class="mb-4">Most recent photos appear first.</Detail>
            <Card>
                <div class="flex flex-row flex-wrap gap-1">
                    <div class="w-20 h-20 bg-zinc-200 rounded-[8px]"></div>
                    <div class="w-20 h-20 bg-zinc-200 rounded-[8px]"></div>
                    <div class="w-20 h-20 bg-zinc-200 rounded-[8px]"></div>
                    <div class="w-20 h-20 bg-zinc-200 rounded-[8px]"></div>
                    <div class="w-20 h-20 bg-zinc-200 rounded-[8px]"></div>
                    <div class="w-20 h-20 bg-zinc-200 rounded-[8px]"></div>

                </div>
            </Card>
        </Padding>
    )
}