import os
import mann2.model_watts

def main():
    # initialize the model
    model = mann2.model_watts.ModelWatts('config_model_watts.yaml',
                                         'model_watts')

    # setup model
    model.setup_model_graph()
    model.setup_model_run()
    output_f_agent_step_info = open(
        model.config['single_sim']['agent_output_file'], 'w')
    output_f_agent_step_info.write('{},{},{},{}\n'.format(
        'time', 'gid', 'aid', 'state'))
    model.run_model(output_f_agent_step_info)
    model.clean_up(output_f_agent_step_info)

    output_f_agent_step_info.close()

if __name__ == '__main__':
    main()
