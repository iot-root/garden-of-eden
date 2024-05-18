import Padding from "@/components/containers/padding"
import { Add } from "@/components/ui/add"
import { Detail, H1 } from "@/typography/heading"
import { Card } from "../ui/card"

export const Camera = () => {
    return (
        <Padding>
            <div class="flex flex-row justify-between items-center">
                <H1>Camera</H1>
                <Add label="Capture" />
            </div>
            <Detail class="mb-4">Most recent photos appear first.</Detail>
            <Card>
                <div class="flex flex-row flex-wrap gap-1">
                    <div class="w-20 h-20 bg-zinc-400 rounded-[8px]"></div>
                    <div class="w-20 h-20 bg-zinc-400 rounded-[8px]"></div>
                    <div class="w-20 h-20 bg-zinc-400 rounded-[8px]"></div>
                    <div class="w-20 h-20 bg-zinc-400 rounded-[8px]"></div>
                    <div class="w-20 h-20 bg-zinc-400 rounded-[8px]"></div>
                    <div class="w-20 h-20 bg-zinc-400 rounded-[8px]"></div>

                </div>
            </Card>
        </Padding>
    )
}