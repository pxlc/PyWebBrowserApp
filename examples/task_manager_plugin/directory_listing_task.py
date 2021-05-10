
import os
import time


def directory_listing_task_validation(task_name, task_data, ui_message_fn, LogLevels):

    print('')
    print('>>> In directory_listing_task_validation() function')
    print('')

    folder_path = os.path.expandvars(task_data.get('folder_path', '')).strip().replace('\\', '/')

    if not folder_path or not os.path.exists(folder_path):
        message = 'Folder path "' + folder_path + '" is empty or does not exist.'
        ui_messsage_fn(message, LogLevels.ERROR)
        return False

    if not os.path.isdir(folder_path):
        message = 'Folder path "' + folder_path + '" is not a directory.'
        ui_messsage_fn(message, LogLevels.ERROR)
        return False

    return True


def directory_listing_task(task_name, task_data, ui_message_fn, ui_update_progress_fn, ui_task_ended_fn,
                           LogLevels, TaskStatuses):

    print('')
    print('>>> In directory_listing_task() function')
    print('')

    folder_path = os.path.expandvars(task_data.get('folder_path', '')).strip().replace('\\', '/')

    starting_msg = '\n'.join([
        '',
        '---------------------------------------------------',
        '  Starting Processing for folder path:',
        '    %s' % folder_path,
        '---------------------------------------------------',
        '',
    ])
    ui_message_fn(starting_msg, LogLevels.INFO)
    ui_update_progress_fn(0.0)

    item_list = sorted(os.listdir(folder_path))
    num_items = len(item_list)

    for idx, item in enumerate(item_list):
        item_path = '%s/%s' % (folder_path, item)
        ui_message_fn('>> Processing folder item: %s' % item, LogLevels.INFO)

        time.sleep(1)

        if os.path.isfile(item_path):
            ui_message_fn('   ... is a File', LogLevels.INFO)
        elif os.path.isdir(item_path):
            ui_message_fn('   ... is a Directory', LogLevels.INFO)
        else:
            ui_message_fn('   ... is a ????', LogLevels.INFO)

        percent_complete = (float(idx+1) / float(num_items)) * 100.0 + 0.5
        ui_update_progress_fn(percent_complete)

    completion_msg = '\n'.join([
        '',
        '---------------------------------------------------',
        '  Processing of folder path:',
        '    %s' % folder_path,
        '  ... COMPLETED.',
        '---------------------------------------------------',
    ])
    ui_message_fn(completion_msg, LogLevels.INFO)
    ui_task_ended_fn(TaskStatuses.COMPLETED, 'processing completed successfully')

    return TaskStatuses.COMPLETED


