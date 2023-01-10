#!/usr/bin/python2
# This is based heavily on https://github.com/aventuri/opencaster/blob/4640061659c1fefe15bcb5251946d9900916a532/tutorials/hbbtv/hbbtv-http.py#L20

from click import command, IntRange, option
from dvbobjects.MHP.AIT import (
    application_information_section
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
def mux_hbbtv(
    video_pid, audio_pid, hbbtv_pid, video_ts, audio_ts, network_id, service_id, network_name,
    pmt_pid, provider_name, service_name
):
    """
    Multiplexes a single video, audio and HbbTV feed for transmission
    """
    
    nit = network_information_section(
        network_id = network_id,
        network_descriptor_loop = [
	        network_descriptor(network_name = network_name,), 
        ],
        transport_stream_loop = [
            transport_stream_loop_item(
                transport_stream_id = 1,
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
                        service_provider_name = provider_name,
                        service_name = service_name,
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
        common_descriptor_loop = [
		external_application_authorisation_descriptor(
			application_identifiers = [[organisationId_1,applicationId_1] , [organisationId_2,applicationId_2]],
			application_priority =     [  			5			          ,		 		1			      ]
			# This descriptor informs that 2 applications are available on the program by specifying the applications identifiers (couple of organization_Id and application_Id parameters) and their related priorities (5 for the first and 1 for the second).
			# Actualy our service contains only one application so this descriptor is not relevent and is just here to show you how to use this descriptor.
			# This descriptor is not mandatory and you could remove it (i.e. common_descriptor_loop = []).
			) 
		],
        application_loop = [
		application_loop_item(
			organisation_id = organisationId_1,  # this is a demo value, dvb.org should assign an unique value
			application_id = applicationId_1, 
			
			application_control_code = 1, 
						# 2 is PRESENT, the decoder will add this application to the user choice of application
						# 1 is AUTOSTART, the application will start immedtiatly to load and to execute
						# 7 is DISABLED, The application shall not be started and attempts to start it shall fail.
						# 4 is KILL, it will stop execute the application
			application_descriptors_loop = [
				transport_protocol_descriptor(
					protocol_id = 0x0003, # HTTP transport protocol
					URL_base = appli_root,
					URL_extensions = [],
					transport_protocol_label = 3, # HTTP transport protocol
				),  
				application_descriptor(
					application_profile = 0x0000,
						#0x0000 basic profile
						#0x0001 download feature
						#0x0002 PVR feature
						#0x0004 RTSP feature
					version_major = 1, # corresponding to version 1.1.1
					version_minor = 1,
					version_micro = 1,
					service_bound_flag = 1, # 1 means the application is expected to die on service change, 0 will wait after the service change to receive all the AITs and check if the same app is signalled or not
					visibility = 3, # 3 the applications is visible to the user, 1 the application is visible only to other applications
					application_priority = 1, # 1 is lowset, it is used when more than 1 applications is executing
					transport_protocol_labels = [3], # If more than one protocol is signalled then each protocol is an alternative delivery mechanism. The ordering indicates 
													 # the broadcaster's view of which transport connection will provide the best user experience (first is best)
				),
				application_name_descriptor(
					application_name = appli_name,
					 ISO_639_language_code = "FRA"
				),
				simple_application_location_descriptor(initial_path_bytes = appli_path),		
			]
		),
		
   	],
        version_number = 1,
        section_number = 0,
        last_section_number = 0,
	)

if __name__ == "__main__":
    mux_hbbtv()
