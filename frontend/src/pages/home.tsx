import { Camera } from "@/components/content/camera"
import { Logs } from "@/components/content/logs"
import { Notifications } from "@/components/content/notifications"
import { Schedule } from "@/components/content/schedule"
import Sensors from "@/components/content/sensors"

export default () => {
    return (
        <>
            {/* Mobile */}
            <div class="lg:hidden">
                <Sensors />
                <Schedule />
            </div>

            {/* Lg */}
            <div class="p-8 2xl:hidden">
                <div class="hidden lg:block ">
                    <div class="hidden lg:grid grid-cols-2 mb-10">
                        <div>
                            <Sensors />
                        </div>
                        <div>
                            <Schedule />
                            <Notifications />
                        </div>
                    </div>

                    <div class="hidden lg:grid lg:grid-cols-2 mb-10">
                        <Camera />
                    </div>

                </div>
                <div class="hidden lg:flex flex-col">
                    <Logs />
                </div>
            </div>

            {/* 2Xl */}
            <div class="hidden 2xl:block p-8">
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