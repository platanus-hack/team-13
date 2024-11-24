provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "ec2_hackathon" {
  ami                    = "ami-0cd59ecaf368e5ccf"
  instance_type          = "t3.medium"
  key_name               = "key-for-hackathon"
  vpc_security_group_ids = [aws_security_group.main.id]

  provisioner "remote-exec" {
    inline = ["echo 'Wait until SSH is ready'"]
    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file("~/.ssh/hackathon")
      host        = self.public_ip
    }
  }

  provisioner "local-exec" {
    command = "ansible-playbook -i ${self.public_ip}, --private-key ~/.ssh/hackathon ./ansible_common/setup.yaml"
  }
}

resource "aws_security_group" "main" {
  egress = [
    {
      cidr_blocks      = ["0.0.0.0/0"]
      description      = ""
      from_port        = 0
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "-1"
      security_groups  = []
      self             = false
      to_port          = 0
    }
  ]
  ingress = [
    {
      cidr_blocks      = ["0.0.0.0/0"]
      description      = ""
      from_port        = 22
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "tcp"
      security_groups  = []
      self             = false
      to_port          = 22
    },
    {
      cidr_blocks      = ["0.0.0.0/0"]
      description      = ""
      from_port        = 80
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "tcp"
      security_groups  = []
      self             = false
      to_port          = 80
    },
    {
      cidr_blocks      = ["0.0.0.0/0"]
      description      = "Allow HTTP traffic on port 8000"
      from_port        = 8000
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "tcp"
      security_groups  = []
      self             = false
      to_port          = 8000
    },
    {
      cidr_blocks      = ["0.0.0.0/0"]
      description      = "Allow HTTPS traffic"
      from_port        = 443
      ipv6_cidr_blocks = []
      prefix_list_ids  = []
      protocol         = "tcp"
      security_groups  = []
      self             = false
      to_port          = 443
    }
  ]
}


resource "aws_key_pair" "deployer" {
  key_name   = "key-for-hackathon"
  public_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBGW96cmV1ntXeKG/lexB0VJMuSyGx1uBYM3Y0rUPXEV hackathon@devs.com"
}
