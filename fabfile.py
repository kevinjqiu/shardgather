from fabric.api import local


def coverage():
    local('coverage run --branch --source shardgather $(which nosetests)')
    local('coverage combine')
    local('coverage report')
