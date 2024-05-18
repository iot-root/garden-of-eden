import { Button } from "@/components/ui/button"
import Padding from "../containers/padding"
import { Card } from "../ui/card"
import { Checkbox } from "../ui/checkbox/checkbox"

export const CreateSchedule = () => {
    return (
        <Padding>
            <Card class="flex flex-col justify-start items-start">
                <div class="flex flex-col items-start mb-8">
                    <p class="font-bold">Create Schedule</p>
                    <p class="text-sm text-zinc-400">Change the details of this schedule.</p>
                </div>

                <div class="flex flex-col items-start mb-8 w-full">
                    <p class="font-medium mb-2">Days</p>

                    <div class="flex flex-row justify-between w-[80%]">
                        <div>
                            <Checkbox label="Monday" />
                            <Checkbox label="Tuesday" />
                            <Checkbox label="Wednesday" />
                            <Checkbox label="Thursday" />
                        </div>
                        <div>
                            <Checkbox label="Friday" />
                            <Checkbox label="Saturday" />
                            <Checkbox label="Sunday" />
                        </div>
                    </div>
                </div>

                <div class="mb-8">
                    <p class="font-medium mb-2">Time</p>
                </div>

                <div class="mb-8 flex flex-col items-start">
                    <p class="font-medium mb-2">Lights</p>
                    <p class="font-light">Run</p>
                    <p class="font-light">Duration</p>
                    <p class="font-light">Brightness</p>
                </div>

                <div class="font-medium mb-8 flex flex-col items-start">
                    <p class="font-medium mb-2">Pump</p>
                    <p class="font-light">Run</p>
                    <p class="font-light">Duration</p>
                    <p class="font-light">Speed</p>
                </div>

                <div class="mb-8 flex flex-col items-start">
                    <p class="font-medium mb-2">Log</p>
                    <p class="font-light">Temp</p>
                    <p class="font-light">Humidity</p>
                    <p class="font-light">PCB Temp</p>
                </div>

                <div class="flex flex-row justify-between w-full">
                    <Button variant="destructive">Delete</Button>
                    <Button>Save</Button>
                </div>
            </Card>
        </Padding>
    )
}