FROM ponggongkong/dynaphish:1
# https://hub.docker.com/repository/docker/ponggongkong/dynaphish/general

#  Expose the port 5000 of the docker container
EXPOSE 5000

COPY . /root/Dynaphish/
WORKDIR /root/Dynaphish
RUN conda init bash

CMD ["/bin/bash"]
# Set up the entrypoint script
RUN chmod +x /root/Dynaphish/entrypoint.sh
ENTRYPOINT ["/root/Dynaphish/entrypoint.sh"]