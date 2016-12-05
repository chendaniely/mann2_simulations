# import os
import mann2.model_lens_attitudeDiffusion


def main():
    # initialize the model
    model = mann2.model_lens_attitudeDiffusion.ModelLensAttitudeDiffusion(
        config_file='config_model_lens_recurrent_attitudeDiffusion.yaml',
        logger_name='model_lens_recurrent_attitudeDiffusion')

    # setup model
    model.setup_model_graph()
    model.setup_model_run()

    output_f_agent_step_info = open(model.config['single_sim']['agent_output_file'], 'w')

    model.setup_output_file(output_f_agent_step_info)
    model.run_model(output_f_agent_step_info)

    model.clean_up(output_f_agent_step_info)

    output_f_agent_step_info.close()

if __name__ == '__main__':
    main()
