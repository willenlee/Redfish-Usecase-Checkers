# Copyright Notice:
# Copyright 2017 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Usecase-Checkers/blob/master/LICENSE.md

import redfish
import traceback
import sys
import os
from power_control import perform_power_control, main_arg_setup

sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])) + '/..')

from usecase.results import Results


def main(argv):
    argget = main_arg_setup()

    argget.add_argument('--output_result', default='./', type=str,
                        help='output directory for test information results.json')

    args = argget.parse_args()

    output_dir = args.output_result

    argsList = [argv[0]]
    for name, value in vars(args).items():
        if name == "password":
            argsList.append(name + "=" + "********")
        else:
            argsList.append(name + "=" + str(value))

    # Set up the Redfish object
    base_url = "https://" + args.rhost
    if args.Secure == "Never":
        base_url = "http://" + args.rhost

    try:
        redfish_obj = redfish.redfish_client(
            base_url=base_url, username=args.user, password=args.password, default_prefix="/redfish/v1")
        redfish_obj.login(auth=args.auth)
    except Exception as e:
        print('Exception has occurred when creating redfish object')
        print(traceback.format_exc(2))
        return 1

    service_root = redfish_obj.get("/redfish/v1/", None)
    success = service_root.status in [200, 204]

    pc_results = []

    if success:
        pc_results = perform_power_control(
            args.target_systems, redfish_obj, args.shutdown_type, args.delay)

    # create results object
    results = Results(
        "Power Control", service_root.dict if success else dict())
    results.add_cmd_line_args(argsList)
    if output_dir is not None:
        results.set_output_dir(output_dir)

    if not success:
        results.update_test_results(
            'ServiceRoot', 1, "ServiceRoot is not available")
        cntSuccess = -1
        print("ServiceRoot is not available")
    else:
        cntSuccess = 0
        for res in pc_results:
            if(res[0]):
                cntSuccess += 1
            results.update_test_results(
                'System Tested', 0 if res[0] else 1, res[1])
        if (args.output_result):
            print('{} out of {} systems passed'.format(
                cntSuccess, len(pc_results)))

    if (args.output_result):
        results.write_results()

    redfish_obj.logout()
    return 0 if cntSuccess == len(pc_results) else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
main(sys.argv)
