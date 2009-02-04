# the idea of this script is to create a mockup of a blog site, with (by
# default) 100 posts and fill each post with a 10 paragraph lorem ipsum.
# 
# On my machine (MBP 2.2Ghz) it can serve upto 18.7 requests per second,
# using the following request with ab:
#
#   ab -c 3 -n 1000 'http://test.local/~rolando/'
#
# for each individual post, the rps is constant in time, no matter how
# many entries you might have.
# 
# With 1000 posts (in the same machine), it went down to 11.6 requests
# per second... very nice for a 1 file blog script :-)
#
# Oh, btw... these benchmarks were made using ruby 1.9.1:
# 
#   ruby 1.9.1p0 (2009-01-20 revision 21700) [i386-darwin9.6.0]
#
# :-)

lipsum = <<-EOS
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce ultricies augue vitae urna. Pellentesque rhoncus sem et augue. Nullam elementum lectus in arcu luctus sollicitudin. Mauris et massa. In euismod lorem a lacus. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras tellus nulla, consectetur vestibulum, commodo tempus, lacinia eget, elit. Curabitur dignissim magna eu quam. Quisque aliquam porttitor dolor. Sed dictum odio ac mauris. Suspendisse potenti. Fusce ut metus. Morbi rhoncus, nunc pulvinar feugiat ultrices, felis dui suscipit est, sit amet fermentum magna felis ut dui. Maecenas varius, mauris quis commodo vehicula, diam massa varius ligula, ut ornare tortor quam in odio. Aenean eget enim eget metus eleifend aliquet. In dictum, magna et congue volutpat, nisi purus pellentesque ante, eu adipiscing neque leo at erat. Ut vitae risus. Nam id lacus vel diam adipiscing posuere. Cras molestie mi vel velit. Donec justo ante, semper lacinia, malesuada nec, porttitor sed, sapien.
Curabitur sit amet urna. Vestibulum gravida mollis velit. Nam fermentum consectetur augue. Aliquam dictum, mi sit amet malesuada facilisis, lectus justo adipiscing dui, vel fermentum elit elit eget risus. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Fusce tempor blandit justo. Vestibulum ligula turpis, venenatis quis, pretium et, varius id, lectus. Aenean nibh. Sed varius cursus dolor. Donec hendrerit. Vestibulum condimentum neque et nisl mattis dictum.
Donec non massa id justo pellentesque mattis. Donec quam. Aliquam vehicula lectus sed quam. Nunc in sem ac urna sagittis gravida. Morbi eu lacus ac nulla venenatis blandit. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Donec aliquam. Nulla facilisi. Proin a magna. Praesent vel nisi. Proin ultrices accumsan magna. Maecenas molestie posuere nisl. Vestibulum id urna. Nulla facilisi. Donec venenatis felis a pede. Sed pede tellus, porta eu, sodales a, euismod vel, orci. Aenean nulla mi, porttitor quis, elementum quis, feugiat vel, ligula. Nunc sed dui. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae;
Nunc sed metus ut quam mattis pharetra. Suspendisse nunc. Curabitur vel lorem at enim porttitor egestas. Nullam varius sem ut pede. Maecenas ultrices lacus. Aliquam tempor arcu sed pede. Integer a libero ac dui fermentum facilisis. Fusce convallis augue id turpis. Sed sollicitudin placerat mauris. Sed porttitor tellus sed tellus. Nulla eget mauris eu odio laoreet porttitor. Donec metus sem, laoreet et, pulvinar nec, tincidunt vel, lacus. In vehicula nunc non sapien. Phasellus dui nulla, egestas sed, placerat eget, sodales eu, massa. In cursus. Suspendisse potenti. Praesent sit amet ligula id purus ornare aliquet.
Phasellus pharetra convallis nisi. Curabitur vulputate tincidunt justo. Curabitur lacus justo, hendrerit in, adipiscing in, suscipit sit amet, turpis. Etiam viverra lectus in nunc. Quisque lectus. Nulla nec massa id dolor porttitor luctus. Mauris imperdiet. Vivamus ut augue a nunc molestie scelerisque. Mauris justo. Nunc vel lectus eu ipsum ultricies convallis. Nulla dapibus. Vestibulum commodo arcu at erat. Sed sed elit sit amet turpis ultricies tempus. Morbi dictum. Nulla ornare felis eget est.
Etiam fermentum nibh eu pede. Aliquam velit. Nunc eu odio vel elit suscipit egestas. Vestibulum sed felis ut arcu congue tincidunt. Proin eros mi, lobortis sed, fringilla id, tempus a, metus. Sed dictum fringilla velit. Cras quis arcu quis dolor luctus rhoncus. Donec non erat id felis fermentum venenatis. Phasellus dapibus. Nunc eros. Vestibulum pharetra tellus nec massa.
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi malesuada rutrum turpis. Phasellus dolor leo, rutrum in, feugiat vitae, accumsan a, augue. Proin in pede nec nunc placerat dapibus. Integer sagittis, mauris vitae tristique sollicitudin, enim diam pharetra orci, quis sollicitudin nisi quam et purus. Praesent ultrices eleifend est. Cras viverra est non elit. Suspendisse non velit. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. In nisl dolor, aliquet at, bibendum vel, vestibulum ut, lorem. Nunc magna magna, varius eu, fringilla eu, blandit condimentum, tortor. Praesent malesuada tristique orci. Vivamus at dolor quis ligula ornare lobortis. Donec rhoncus porta ante.
Curabitur ligula leo, fringilla eget, pellentesque at, interdum ut, purus. Curabitur fermentum faucibus diam. Aenean tincidunt ligula vel pede. Pellentesque pellentesque urna eget justo. Fusce pharetra sapien at lacus faucibus convallis. Maecenas gravida. Proin nunc. Suspendisse mattis ultrices nibh. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Pellentesque a leo. Proin fermentum blandit magna. Maecenas ornare pede eu nisl. Ut in nisi eu orci laoreet fermentum. Phasellus commodo aliquet dui. Ut arcu erat, scelerisque sed, dignissim ac, aliquam eu, massa. Phasellus accumsan, magna pretium commodo sodales, velit metus pretium tortor, nec pretium purus magna a risus. Proin eu mauris.
Aenean imperdiet iaculis justo. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Aenean adipiscing ipsum eget libero. Pellentesque suscipit rutrum justo. Sed quis magna. Phasellus rutrum metus in nibh. Donec diam ante, lobortis a, venenatis vitae, dignissim consectetur, nulla. Duis vel diam. Duis augue mauris, ultricies ac, tempus eget, mollis vel, velit. Vestibulum purus. Vestibulum tincidunt mi vel mi. Nam lorem. Nullam venenatis fermentum lorem. Quisque odio nunc, lacinia sit amet, accumsan non, faucibus id, lorem.
Aliquam ultrices massa sit amet neque. Duis egestas consectetur nibh. Pellentesque bibendum euismod dolor. Nunc et ipsum. Fusce ante. Etiam ac mauris. Proin egestas ipsum. Nunc vitae enim. Aliquam sed est sed pede porttitor mollis. Ut aliquam. Mauris cursus. Nullam justo. Curabitur velit ligula, ultrices vel, viverra ac, laoreet ut, felis. Phasellus libero ante, pellentesque ut, tincidunt quis, pretium quis, enim.
EOS

lipsum_arr = lipsum.split(/\n/)
dir   = ARGV[0]                # where to create the fake site
total = (ARGV[1] || 100).to_i  # total number of entries
depth = (ARGV[2] || 3).to_i    # max depth of tree

require 'fileutils'
include FileUtils

total.downto(1) do |post_no|
  cur_depth = (depth > 1) ? ((rand * (depth - 1)).round + 1) : 1
  cur_dir = (1 .. cur_depth).inject([]) { |s,i| s << "dir#{i}" }.join("/")
  mkdir_p "#{dir}/#{cur_dir}"
  File.open("#{dir}/#{cur_dir}/post_#{post_no}.txt", "w+") { |f|
    f.write lipsum
  }
end
