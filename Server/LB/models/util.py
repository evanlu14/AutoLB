from ansible import playbook, callbacks

# namespace
def _create_ns(ns_name):
    stats = _run_playbook(
        playbook_path='/SOME/PATH/book.yml',
        hosts_path='/SOME/OTHER/PATH/ansible_hosts',
        key_file='/OTHER/PATH/keys/id_rsa.pub')
    pass

def _get_ns_name(user, proj_name, id):
    if isinstance(id, int):
        id = str(id)
    return user + "_" + proj_name + "_" + id

# vm
def _create_vm(vm_name):
    pass

def _get_vm_name(user, proj_name, id):
    return user + proj_name + id

# ansible
def _run_playbook(playbook_path, hosts_path, key_file):
    stats = callbacks.AggregateStats()
    playbook_cb = callbacks.PlaybookCallbacks(verbose=0)
    runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=0)
    playbook.PlayBook(
        playbook=playbook_path,
        host_list=hosts_path,
        stats=stats,
        forks=4,
        callbacks=playbook_cb,
        runner_callbacks=runner_cb,
        private_key_file=key_file
        ).run()
    return stats
