import { Camera } from "@/components/content/camera"
import { Logs } from "@/components/content/logs"
import { Notifications } from "@/components/content/notifications"
import { Schedule } from "@/components/content/schedule"
import Sensors from "@/components/content/sensors"

export default () => {
    return (
        <>
            {/* Mobile */}
            <div class="md:hidden w-full">
                <Sensors />
                <Schedule />
            </div>

            {/* Md*/}
            <div class="hidden md:block p-8 lg:hidden">
                <div class="md:grid grid-cols-2 mb-10">
                    <div>
                        <Sensors />
                    </div>
                    <div>
                        <Schedule />
                        <Notifications />
                    </div>
                </div>

                <div class="md:grid lg:grid-cols-2 mb-10">
                    <Camera />
                </div>

                <div class="md:flex flex-col">
                    <Logs />
                </div>
            </div>

            {/* Lg */}
            <div class="hidden lg:block p-8 xl:hidden">
                <div class="grid grid-cols-2 mb-10">
                    <div>
                        <Sensors />
                    </div>
                    <div>
                        <Schedule />
                        <Notifications />
                    </div>
                </div>

                <div class="grid grid-cols-1 mb-10">
                    <Camera />
                </div>

                <div class="flex flex-col">
                    <Logs />
                </div>
            </div>

            {/* Xl */}
            <div class="hidden xl:block p-8">
                <div class="hidden lg:block">
                    <div class="hidden lg:grid grid-cols-3 mb-10">
                        <div class="col-span-1">
                            <Sensors />
                            <Schedule />
                            <Notifications />
                        </div>
                        <div class="col-span-2">
                            <Camera />
                            <Logs />
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
}