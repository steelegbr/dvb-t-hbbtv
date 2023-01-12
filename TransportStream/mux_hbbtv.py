#!/usr/bin/python2
# This is based heavily on https://github.com/aventuri/opencaster/blob/4640061659c1fefe15bcb5251946d9900916a532/tutorials/hbbtv/hbbtv-http.py#L20

from click import command, IntRange, option
from dvbobjects.HBBTV.Descriptors import (
    application_descriptor,
    application_name_descriptor,
    simple_application_location_descriptor,
    transport_protocol_descriptor,
)
from dvbobjects.MHP.AIT import (
    application_information_section,
    application_loop_item,
)
from dvbobjects.PSI.NIT import (
    network_descriptor,
    network_information_section,
    service_descriptor_loop_item,
    service_list_descriptor,
    transport_stream_loop_item,
)
from dvbobjects.PSI.PAT import (
    program_association_section,
    program_loop_item,
)
from dvbobjects.PSI.PMT import (
    application_signalling_descriptor,
    program_map_section,
    stream_loop_item,
)
from dvbobjects.PSI.SDT import (
    service_description_section,
    service_descriptor,
    service_loop_item,
)
from os import system

@command()
@option("--video-pid", prompt="PID for the video stream", type=IntRange(1, 8191))
@option("--audio-pid", prompt="PID for the audio stream", type=IntRange(1, 8191))
@option("--hbbtv-pid", prompt="PID for the video stream", type=IntRange(1, 8191))
@option("--pmt-pid", prompt="PID for the PMT", type=IntRange(1, 8191))
@option("--video-ts", prompt="Transport Stream video file")
@option("--audio-ts", prompt="Transport Stream audio file")
@option("--network-id", prompt="The ID for the network", default=1)
@option("--service-id", prompt="The service ID for the broadcast", default=1)
@option("--network-name", prompt="The name for the TV network", default="TestTV")
@option("--provider-name", prompt="The HbbTV provider name", default="researchmux")
@option("--service-name", prompt="The HbbTV service name", default="HbbTvTest")
@option("--org-id", prompt="The organisation ID", type=int, default=10)
@option("--app-id", prompt="The application ID", type=int, default=1001)
@option("--app-name", prompt="The name of the application", default="Research App")
@option("--app-path", prompt="The path to the application")
@option("--ait-pid", prompt="PID for the Application Information Table", type=IntRange(1, 8191))
@option("--output", prompt="Output file path")
def mux_hbbtv(
    video_pid, audio_pid, hbbtv_pid, video_ts, audio_ts, network_id, service_id, network_name,
    pmt_pid, provider_name, service_name, org_id, app_id, app_name, app_path, ait_pid, output
):
    """
    Multiplexes a single video, audio and HbbTV feed for transmission
    """
    
    nit = network_information_section(
        network_id = network_id,
        network_descriptor_loop = [
	        network_descriptor(network_name = str(network_name),), 
        ],
        transport_stream_loop = [
            transport_stream_loop_item(
                transport_stream_id = 1,
                original_network_id = network_id,
                transport_descriptor_loop = [
                    service_list_descriptor(
                        dvb_service_descriptor_loop = [
                            service_descriptor_loop_item(
                                service_ID = service_id, 
                                service_type = 1,
                            ),
                        ],
                    ),
                ],		
            ),
        ],
        version_number = 1,
        section_number = 0,
        last_section_number = 0,
    )

    pat = program_association_section(
        transport_stream_id = service_id,
        program_loop = [
            program_loop_item(
                program_number = service_id,
                PID = pmt_pid,
            ),  
            program_loop_item(
                program_number = 0,
                PID = 16,
            ), 
        ],
        version_number = 1,
        section_number = 0,
        last_section_number = 0,
    )

    pmt = program_map_section(
        program_number = service_id,
        PCR_PID = video_pid, # usualy the same than the video
        program_info_descriptor_loop = [],
        stream_loop = [
            stream_loop_item(
                stream_type = 2, # mpeg2 video stream type
                elementary_PID = video_pid,
                element_info_descriptor_loop = []
            ),
            stream_loop_item(
                stream_type = 3, # mpeg2 audio stream type
                elementary_PID = audio_pid,
                element_info_descriptor_loop = []
            ),
            stream_loop_item(
                stream_type = 5, # AIT stream type
                elementary_PID = hbbtv_pid,
                element_info_descriptor_loop = [ 
                    application_signalling_descriptor(
                        application_type = 0x0010, # HbbTV service
                        AIT_version = 1,  # current ait version
                    ),
                ]	
            ),		
        ],
        version_number = 1, # you need to change the table number every time you edit, so the decoder will compare its version with the new one and update the table
        section_number = 0,
        last_section_number = 0,
    )  

    sdt = service_description_section(
        transport_stream_id = network_id,
        original_network_id = network_id,
        service_loop = [
            service_loop_item(
                service_ID = service_id,
                EIT_schedule_flag = 0, # 0 no current even information is broadcasted, 1 broadcasted
                EIT_present_following_flag = 0, # 0 no next event information is broadcasted, 1 is broadcasted
                running_status = 4, # 4 service is running, 1 not running, 2 starts in a few seconds, 3 pausing
                free_CA_mode = 0, # 0 means service is not scrambled, 1 means at least a stream is scrambled
                service_descriptor_loop = [
                    service_descriptor(
                        service_type = 1, # digital television service
                        service_provider_name = str(provider_name),
                        service_name = str(service_name),
                    ),    
                ],
            ),	
        ],
        version_number = 1, # you need to change the table number every time you edit, so the decoder will compare its version with the new one and update the table
        section_number = 0,
        last_section_number = 0,
    )

    ait = application_information_section(
        application_type = 0x0010,
        common_descriptor_loop = [],
        application_loop = [
			application_loop_item(
				organisation_id = org_id,  # this is a demo value, dvb.org should assign an unique value
				application_id = app_id, 
				application_control_code = 1, 
				application_descriptors_loop = [
					transport_protocol_descriptor(
							protocol_id = 0x0001, # the application is broadcasted on a DSMCC
							transport_protocol_label = 1, # the application is broadcasted on a DSMCC
							remote_connection = 0, # shall be 0 for HbbTV 
							component_tag = 0xB, # carousel common tag and association tag
					),
					application_descriptor(
							application_profile = 0x0000, 
							version_major = 1, # corresponding to version 1.1.1
							version_minor = 1,
							version_micro = 1,
							service_bound_flag = 1, # 1 means the application is expected to die on service change, 0 will wait after the service change to receive all the AITs and check if the same app is signalled or not
							visibility = 3, # 3 the applications is visible to the user, 1 the application is visible only to other applications
							application_priority = 1, # 1 is lowset, it is used when more than 1 applications is executing
							transport_protocol_labels = [1], # carousel Id
					),
					application_name_descriptor(application_name = str(app_name)),
					simple_application_location_descriptor(initial_path_bytes = str(app_path)),
				]
			),
		],
        version_number = 1,
        section_number = 0,
        last_section_number = 0,
	)

    out = open("./nit.sec", "wb")
    out.write(nit.pack())
    out.close
    out = open("./nit.sec", "wb") # python  flush bug
    out.close
    system('/usr/bin/sec2ts 16 < ./nit.sec > ./Media/nit.ts')

    out = open("./pat.sec", "wb")
    out.write(pat.pack())
    out.close
    out = open("./pat.sec", "wb") # python   flush bug
    out.close
    system('/usr/bin/sec2ts 0 < ./pat.sec > ./Media/pat.ts')

    out = open("./sdt.sec", "wb")
    out.write(sdt.pack())
    out.close
    out = open("./sdt.sec", "wb") # python   flush bug
    out.close
    system('/usr/bin/sec2ts 17 < ./sdt.sec > ./Media/sdt.ts')

    out = open("./pmt.sec", "wb")
    out.write(pmt.pack())
    out.close
    out = open("./pmt.sec", "wb") # python   flush bug
    out.close
    system('/usr/bin/sec2ts ' + str(pmt_pid) + ' < ./pmt.sec > ./Media/pmt.ts')

    out = open("./ait.sec", "wb")
    out.write(ait.pack())
    out.close
    out = open("./ait.sec", "wb") # python   flush bug
    out.close
    system('/usr/bin/sec2ts ' + str(ait_pid) + ' < ./ait.sec > ./Media/ait.ts')

    system(
        '/usr/bin/tscbrmuxer b:2300000 {0} b:188000 {1} b:3008 ./Media/pat.ts b:3008 ./Media/pmt.ts b:1500 ./Media/sdt.ts b:1400 ./Media/nit.ts b:2000 ./Media/ait.ts b:8770084 ./Media/null.ts > {2}'.format(
            video_ts,
            audio_ts,
            output
        )
    )

    system('rm *.sec')

if __name__ == "__main__":
    mux_hbbtv()
